import streamlit as st
from PIL import Image
from transformers import Qwen3VLForConditionalGeneration, AutoProcessor
import torch

st.set_page_config(page_title="Qwen3-VL Doküman Analizi", layout="wide")
st.title("📄 Yapay Zeka ile Doküman Analizi (Qwen3-VL)")
st.markdown("Bir fatura resmi yükleyin ve doküman hakkındaki sorularınızı sorun.")

@st.cache_resource
def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen3-VL-2B-Instruct", attn_implementation = "flash_attention_2", dtype=torch.bfloat16, device_map="auto")
    if device == "cpu":
        model = Qwen3VLForConditionalGeneration.from_pretrained(
            "Qwen/Qwen3-VL-2B-Instruct", dtype="auto", device_map="auto")
    processor = AutoProcessor.from_pretrained("Qwen/Qwen3-VL-2B-Instruct")
    return model, processor, device

with st.sidebar:
    st.header("Sistem Durumu")
    with st.spinner("Model yükleniyor..."):
        model, processor, device = load_model()
    
    if model:
        st.success(f"Model Yüklendi! \nCihaz: {device.upper()}")
    
    st.info("Desteklenen Formatlar: JPG, PNG, JPEG")

uploaded_file = st.file_uploader("Dosya Seçin", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen Belge", use_column_width=True)
    st.divider()
    default_question = "[Örnek Soru]: Vergilendirme dönemi ne zaman?"
    question = st.text_input("Soru Sorun:", value=default_question)
    if st.button("Analiz Et", type="primary"):
        if not model:
            st.error("Model henüz yüklenmedi, lütfen bekleyin.")
        else:
            with st.spinner("Belge okunuyor ve analiz ediliyor..."):
                messages = [
                    {
                            "role": "user",
                            "content": [
                                {"type": "image", "image": image},
                                {"type": "text", "text": question},
                                {"type": "text", "text": f"This image contains Turkish character. Answer the following question: {question}"},
                            ],
                        }
                ]
        
        inputs = processor.apply_chat_template(messages,
                                              tokenize=True,
                                              add_generation_prompt=True,
                                              return_dict=True,
                                              return_tensors="pt")
        inputs = inputs.to(model.device)
        generated_ids = model.generate(**inputs, max_new_tokens=128)
        generated_ids_trimmed = [out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
        output_text = processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        st.success("Sonuç:")
        st.write(output_text[0])