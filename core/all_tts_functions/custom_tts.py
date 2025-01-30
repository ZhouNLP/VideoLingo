from pathlib import Path
# import dashscope
# from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer
import os

# 阿里云灵积模配置
DEFAULT_MODEL = "cosyvoice-clone-v1"
DASHSCOPE_API_KEY = "YOUR_DASHSCOPE_API_KEY"  # 请替换为您的API密钥
voice_id = 'longcheng'

def custom_tts(text: str, save_path: str) -> None:
    """
    使用阿里云灵积模进行TTS转换
    
    Args:
        text (str): 需要转换的文本
        save_path (str): 音频保存路径
    """
    # 确保保存目录存在
    speech_file_path = Path(save_path)
    speech_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # 初始化API密钥
        dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', DASHSCOPE_API_KEY)
        
        # 创建语音合成器实例
        synthesizer = SpeechSynthesizer(model=DEFAULT_MODEL, voice=voice_id)
        
        # 合成音频
        audio = synthesizer.call(text)
        
        # 保存音频文件
        with open(speech_file_path, "wb") as f:
            f.write(audio)
            
        print(f"Audio saved to {speech_file_path}")
        
    except Exception as e:
        print(f"Error occurred during TTS conversion: {str(e)}")
        raise

# 如果需要注册新的声音克隆
def register_new_voice(url: str, prefix: str = "custom"):
    """
    注册新的声音克隆
    
    Args:
        url (str): 用于克隆的音频文件URL
        prefix (str): 音色前缀名
    
    Returns:
        str: voice_id
    """
    try:
        service = VoiceEnrollmentService()
        voice_id = service.create_voice(
            target_model=DEFAULT_MODEL,
            prefix=prefix,
            url=url
        )
        print(f"Successfully registered new voice with ID: {voice_id}")
        return voice_id
        
    except Exception as e:
        print(f"Failed to register new voice: {str(e)}")
        raise

if __name__ == "__main__":
    # 测试示例
    custom_tts("这是一个测试音频。", "custom_tts_test.wav")
