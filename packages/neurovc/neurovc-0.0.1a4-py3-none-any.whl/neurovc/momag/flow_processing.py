__author__ = "Philipp Flotho"
"""
flow_processing
Copyright 2024 by Philipp Flotho, All rights reserved.
"""

from numba import jit
from scipy.spatial import ConvexHull
import PIL
from PIL import ImageDraw

import neurovc
import neurovc as nvc
from neurovc.momag.framewarpers import *
from neurovc.raft import RAFTOpticalFlow
from neurovc.raft.utils.flow_viz import flow_to_image
from neurovc.util.IO_util import CircularFrameBuffer

import mediapipe as mp


def get_motion_magnitude(w):
    return np.sqrt(w[:, :, 0] * w[:, :, 0] + w[:, :, 1] * w[:, :, 1])


def compressive_function(G_mag, alpha, beta):
    eps = 0.1
    beta = 1 - beta
    G_mag[G_mag < eps] = eps
    g_comp = (alpha / G_mag) * np.power((G_mag / alpha), beta)
    g_comp[g_comp < 1] = 1

    return g_comp


class MagnitudeCompressor:
    def __call__(self, w):
        g_mag = np.repeat(get_motion_magnitude(w)[:, :, None], 2, axis=2)
        w /= g_mag + 0.0001
        g_comp = self.comp(g_mag)
        return g_comp * w


class GradMagnitudeCompressor(MagnitudeCompressor):
    def __init__(self, **kwargs):
        self.comp = lambda x: compressive_function(x, **kwargs)


class ConstCompressor(MagnitudeCompressor):
    def __init__(self, alpha):
        self.comp = lambda x: alpha * x


def compressive_function_thresh(G_mag, alpha, threshold):
    g_comp = G_mag
    g_comp[G_mag < threshold] *= alpha
    return g_comp


class ThreshCompressor(MagnitudeCompressor):
    def __init__(self, alpha, threshold):
        self.comp = lambda x: compressive_function_thresh(x, alpha, threshold)


@jit(nopython=True)
def diffusion_loop(img_out, idx, k, h=1):
    for time in range(k):
        for (i, j) in idx:
            img_out[i, j] += (0.25 / (h * h)) * (
                    img_out[i, j + 1] +
                    img_out[i, j - 1] +
                    img_out[i - 1, j] +
                    img_out[i + 1, j] -
                    4 * img_out[i, j])

    return img_out


class FlowDecomposer:
    def __init__(self, landmarks, dims, *idx):
        self.idx = np.array(idx)
        self.dims = dims
        self.mask = None
        self.update_mask(landmarks)

    def update_mask(self, landmarks):
        m, n = self.dims[0:2]
        img = PIL.Image.new('F', (n, m), 0.0)

        for idx in self.idx:
            points = landmarks[idx]
            hull = ConvexHull(points)


            args = np.argsort(hull.simplices, axis=0)
            _, idx = np.unique(hull.simplices[args[:, 0]][:, 0], return_index=True)

            points = [(x, y) for x, y, _ in points[hull.simplices[args[:, 0]][:, 0][idx]]]
            ImageDraw.Draw(img).polygon(points, outline=255, fill=255)

        img = np.array(img)
        circle = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        self.mask = cv2.dilate(img, circle, iterations=16)

    def decompose(self, flow):
        mask_tmp = self.mask # warp_image_pc_single(self.mask, flow)

        flow_global = np.empty(flow.shape, flow.dtype)

        flow_global[:, :, 0] = self.__diffusion(flow[:, :, 0], mask_tmp)
        flow_global[:, :, 1] = self.__diffusion(flow[:, :, 1], mask_tmp)

        flow_local = flow - flow_global

        return flow_global, flow_local

    def __flow_mag(self, flow, normalize=True):
        tmp = np.sqrt(np.multiply(flow[:, :, 0], flow[:, :, 0]) +
                      np.multiply(flow[:, :, 1], flow[:, :, 1]))
        if normalize:
            tmp /= 10.0
            tmp[tmp < 0.0] = 0.0
            tmp[tmp > 1.0] = 1.0

        return tmp

    def __diffusion(self, img, mask):
        idx = np.argwhere(mask != 0)

        img_out = np.empty(img.shape, img.dtype)
        np.copyto(img_out, img)
        img_out = img_out.astype(float)
        img_out[idx[:, 0], idx[:, 1]] = 0

        m, n = img_out.shape
        img_out_low = diffusion_loop(cv2.resize(img_out, (n // 8, m // 8)),
                                     np.argwhere(cv2.resize(mask, (n // 8, m // 8)) != 0), 1000)
        img_out[idx[:, 0], idx[:, 1]] = cv2.resize(img_out_low, (n, m))[idx[:, 0], idx[:, 1]]
        img_out_low = diffusion_loop(cv2.resize(img_out, (n // 4, m // 4)),
                                     np.argwhere(cv2.resize(mask, (n // 4, m // 4)) != 0), 1000)
        img_out[idx[:, 0], idx[:, 1]] = cv2.resize(img_out_low, (n, m))[idx[:, 0], idx[:, 1]]
        img_out[idx[:, 0], idx[:, 1]] = diffusion_loop(img_out, np.argwhere(mask != 0), 500)[idx[:, 0], idx[:, 1]]

        return img_out.astype(img.dtype)


class BasicMagnifier:
    def __init__(self, attenuation_function=None, augmentor=None, mesh_processor=None):
        if augmentor is not None:
            self._augmentor = augmentor
        else:
            self._augmentor = lambda f: f

        if attenuation_function is None:
            self._attenuation_function = ConstCompressor(5)
        else:
            self._attenuation_function = attenuation_function

        self.OF_inst = cv2.DISOpticalFlow.create(cv2.DISOpticalFlow_PRESET_MEDIUM)
        self.OF_inst.setUseSpatialPropagation(True)
        self.OF_inst.setFinestScale(1)
        self.OF_inst.setVariationalRefinementDelta(0.2)
        self.OF_inst.setVariationalRefinementGamma(0.8)
        self.OF_inst.setVariationalRefinementAlpha(0.5)
        self.OF_inst.setVariationalRefinementIterations(5)
        self.mesh_processor = mesh_processor

        self._init = False
        self.ref = None
        self.results_ref = None
        self.last_flow = None

    def _do_init(self, ref):
        m, n = ref.shape[0:2]
        self.framewarper = OnlineFrameWarper((m, n))
        self._init = True

    def update_reference(self, ref, landmarks=None):
        self.ref = ref
        self.results_ref = landmarks
        if landmarks is None and self.mesh_processor is not None:
            self.mesh_processor(ref)
            self.results_ref = self.mesh_processor.last_result[0]

        if not self._init:
            self._do_init(ref)

    def get_flow(self, frame):
        w = self.OF_inst.calc(self._augmentor(self.ref), self._augmentor(frame), self.last_flow)
        self.last_flow = w
        return w

    def __call__(self, frame):
        if not self._init:
            self.update_reference(frame)
        _ = self.get_flow(frame)
        return frame


class AlphaLooper:
    def __init__(self, alpha, step):
        self.alpha = np.arange(alpha[0], alpha[1], 0.5)
        self.idx = 0
        self.__forward = True

    def __call__(self):
        if self.__forward:
            alpha = self.alpha[self.idx]
        else:
            alpha = self.alpha[len(self.alpha) - self.idx - 1]
        self.idx = (self.idx + 1) % len(self.alpha)
        self.__forward = not self.__forward if self.idx == 0 else self.__forward
        return alpha

    def reset(self):
        self.idx = 0
        self.__forward = True


class MagnificationTask:
    def __init__(self):
        self.buffer = CircularFrameBuffer(10)
        self.last_local_flow = None
        self.last_global_flow = None
        self.last_frame = None
        self.last_global_depth = None

        augmentor = lambda f: cv2.cvtColor(f, cv2.COLOR_RGB2GRAY)
        magnifiers = [
            OnlineGlobalMagnifier(augmentor=augmentor),
            OnlineLandmarkMagnifier(nvc.LM_EYE_LEFT,
                                    augmentor=augmentor),
            OnlineLandmarkMagnifier(nvc.LM_EYE_RIGHT,
                                    augmentor=augmentor),
            OnlineLandmarkMagnifier(nvc.LM_FOREHEAD,
                                    augmentor=augmentor),
            OnlineLandmarkMagnifier(landmarks=nvc.LM_MOUTH,
                                    augmentor=augmentor),
        ]

        self.magnifiers = {
            ord(str(i + 1)): magnifier for i, magnifier in enumerate(magnifiers)
        }
        self.current_magnifier = magnifiers[0]

        mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5)

        self.ref = None
        self.results_ref = None

    def __call__(self, frame):
        buf = self.buffer.get_oldest()
        results_frame = self.face_mesh.process(frame)

        self.results_frame = results_frame
        self.last_frame = frame

        if buf is None:
            self.buffer.append((frame, results_frame))
            self.ref = frame
            self.results_ref = results_frame
            return frame
        ref, results_ref = buf
        self.buffer.append((frame, results_frame))
        try:
            self.current_magnifier.update_reference(ref, results_ref)
            self.ref = ref
            self.results_ref = results_ref
            self.update_flow()
        except:
            print("No Landmarks in reference.")

        if results_frame.multi_face_landmarks is None:
            return

        try:
            points = get_landmarks(results_ref)
        except:
            return
        image_size = frame.shape[:2]
        points[:, 0] *= image_size[1]
        points[:, 1] *= image_size[0]
        grid_y, grid_x = np.mgrid[0:image_size[0], 0:image_size[1]]

        global_depth = griddata(points[:, :2], points[:, 2], (grid_x, grid_y), method='linear')
        gd_nan_mask = np.isnan(global_depth)
        global_depth[gd_nan_mask] = global_depth[~gd_nan_mask].max()
        global_depth -= global_depth.min()
        global_depth /= global_depth.max()
        global_depth = 1 - global_depth
        cv2.imshow("depth", global_depth)
        self.last_global_depth = global_depth

    def get_mag(self, alpha):
        if self.last_global_flow is None or self.last_local_flow is None:
            return self.last_frame
        flow = self.last_global_flow + self.last_local_flow
        return self.current_magnifier.framewarper.warp_image_uv(
            warp_image_backwards(self.last_frame, flow),
            self.last_global_flow + alpha * self.last_local_flow,
            self.last_global_depth)

    def update_flow(self):
        try:
            flow_global, flow_local = self.current_magnifier(self.last_frame, self.results_frame)
            self.last_global_flow = flow_global
            self.last_local_flow = flow_local
        except:
            pass

    def set_magnifier(self, key, update_flow=False):
        key = key & 0xFF
        if key in self.magnifiers.keys():
            self.current_magnifier = self.magnifiers[key]
            try:
                self.current_magnifier.update_reference(self.ref, self.results_ref)
            except:
                pass
            if update_flow:
                self.update_flow()


class OnlineGlobalMagnifier(BasicMagnifier):
    def __init__(self, augmentor=None):
        super().__init__(augmentor=augmentor)

    def requires_landmarks(self):
        return False

    def __call__(self, frame, landmarks=None):
        _ = super().__call__(frame)
        return np.zeros_like(self.last_flow), self.last_flow


class OnlineLandmarkMagnifier(BasicMagnifier):
    def __init__(self, landmarks=neurovc.LM_MOUTH, alpha=15, reference=None, attenuation_function=None,
                 augmentor=None):
        super().__init__(attenuation_function=attenuation_function,
                         mesh_processor=FacialMeshProcessor(), augmentor=augmentor)

        mp_drawing = mp.solutions.drawing_utils
        mp_face_mesh = mp.solutions.face_mesh
        self.drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(0, 0, 0))

        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5)

        self._init = False
        self.alpha = alpha

        self.framewarper = None
        self.decomposer = None
        self.ref = None
        self.landmarks = landmarks
        if reference is not None:
            self.update_reference(reference)

    def requires_landmarks(self):
        return True

    def update_reference(self, ref, landmarks=None):
        super().update_reference(ref)
        m, n = ref.shape[0:2]
        self.decomposer = FlowDecomposer(self.mesh_processor.get_last_landmarks(), (m, n),
                                         self.mesh_processor.get_region_from_id(self.landmarks))

    def __call__(self, frame, landmarks=None):
        _ = super().__call__(frame)
        w = self.last_flow
        w_global, w_local = self.decomposer.decompose(w)
        return w_global, w_local

    def get_reference(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_face_mesh = mp.solutions.face_mesh

        lm_viz = self.ref.copy()
        try:
            mp_drawing.draw_landmarks(
                image=lm_viz,
                landmark_list=self.mesh_processor.last_result[0][0],
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=self.drawing_spec,
                connection_drawing_spec=self.drawing_spec)
        except:
            pass
        for x, y, _ in self.mesh_processor.get_last_landmarks()[self.mesh_processor.get_region_from_id(self.landmarks)]:
            cv2.circle(lm_viz, (int(np.round(x)), int(np.round(y))), 5, (0, 0, 255), -1)

        return lm_viz, self.ref


class FacialMeshProcessor:
    mouth_boundary_inner = [167, 164, 393, 391, 322, 410, 287, 273, 335, 406,
                            313, 18, 83, 182, 106, 43, 57, 186, 92, 165]
    mouth_boundary = [203, 98, 97, 2, 326, 327, 423, 426, 436, 432,
                      422, 424, 418, 421, 200, 201, 194, 204, 202, 216, 212, 206]
    mouth_boundary_outer = [203, 98, 97, 2, 326, 327, 423, 425, 427, 430, 434, 431,
                            207, 205, 214, 210, 211,
                            418, 421, 200, 201, 194]
    eye_left_boundary_inner = [225, 224, 223, 222, 221, 189, 244, 233, 232,
                               231, 230, 229, 228, 31, 226, 113]
    eye_right_boundary_inner = [464, 413, 441, 442, 443, 444, 445,
                                342, 446, 448, 449, 450, 451, 452, 453, 261]
    eye_left_boundary = [46, 53, 52, 65, 55, 193, 245, 128, 121, 120, 119,
                         118, 117, 111, 35, 124]
    eye_right_boundary = [285, 417, 465, 357, 350, 349, 348, 347, 346,
                          340, 265, 353, 276, 283, 282, 295]
    forehead_temp_boundary = [109, 69, 66, 65, 55, 8, 285, 295, 282, 334, 333, 332, 297, 338, 10]
    _lms = [mouth_boundary, eye_left_boundary, eye_right_boundary, forehead_temp_boundary]

    def __init__(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_face_mesh = mp.solutions.face_mesh
        self.drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=0, color=(0, 0, 0))

        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5)

        self.last_result = None

    def __call__(self, frame):
        results = self.face_mesh.process(frame)

        m, n = frame.shape[0:2]

        self.last_result = (results, (m, n))

    def get_region_from_id(self, id):
        ids = [1 & (id >> i) for i in range(4)]
        landmark_ids = []
        for i, b in enumerate(ids):
            if b:
                landmark_ids += self._lms[i]
        return landmark_ids

    def get_last_landmarks(self):
        results, (m, n) = self.last_result
        landmark_list = np.array(
            [[n * lm.x, m * lm.y, lm.z] for lm in results.multi_face_landmarks[0].landmark])
        return landmark_list
