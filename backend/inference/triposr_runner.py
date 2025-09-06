import onnx
import onnxruntime as ort

sess = ort.InferenceSession("models/triposr.onnx", providers=["DmlExecutionProvider"])
