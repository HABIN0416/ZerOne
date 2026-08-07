"""
Week 5(통합) - codec.py  :  변환(직렬화·암호화)을 '부품'으로
============================================================
'Codec' 이라는 이름, 어디서 들어봤죠? (동영상 코덱, 오디오 코덱…)
------------------------------------------------------------
Codec = COder + DECoder  (코더 + 디코더)
  - encode(부호화): 보낼 것을 '전송용 형태'로 바꾼다
  - decode(복호화): 받은 것을 '원래 형태'로 되돌린다
  → 이 encode/decode '한 쌍'을 묶은 부품이 코덱이다.

우리가 이미 아는 코덱들:
  · 동영상 코덱(H.264 등): 보낼 땐 압축(encode), 볼 땐 복원(decode)
    "코덱이 없어서 영상이 안 열려요" = decode 할 부품이 없다는 뜻!
  · 오디오 코덱(MP3, AAC): 소리를 작게 담고(encode) 재생 때 되살린다(decode)
  · 1주차의 문자열 .encode()/.decode()(UTF-8)도 사실 '글자 코덱'이었다.

우리 채팅의 코덱도 똑같은 일을 한다:
  · PlainCodec  : 메시지 ↔ 평문 바이트
  · SecretCodec : 메시지 ↔ 암호화 바이트 (XOR + base64)
'무엇으로 바꾸느냐'만 다를 뿐, 전부 encode/decode 한 쌍이다.
------------------------------------------------------------
그리고 이 코덱들은 interfaces.Codec '계약'을 지키는 부품이다.
계약(encode/decode)만 지키면 ChatServer 가 무엇이든 받아 쓴다.
"""
import os
import base64

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from interfaces import Codec
from messages import Message

##XOR로 쓰는 이유 ---> 하나만 날라가도 나머지로 살릴 수 있음

class PlainCodec(Codec):
    name = "평문"

    def encode(self, message): #@abstractmethod로 자식들이 반드시 구현
        return (message.to_wire() + "\n").encode("utf-8")

    def decode(self, line):  #@abstractmethod로 자식들이 반드시 구현
        return Message.from_wire(line) 


SECRET_KEY = 42   # 교육용. 진짜 보안 아님!


def _xor(data, key):
    return bytes(b ^ key for b in data) #데이터에 있는 각 바이트에 대해서 키를 가지고 XOR 시켜줌 


class SecretCodec(Codec):
    name = "암호화(XOR)"

    def __init__(self, key=SECRET_KEY): #암호화 키
        self.key = key

    def encode(self, message):
        scrambled = _xor(message.to_wire().encode("utf-8"), self.key)
        return (base64.b64encode(scrambled).decode("ascii") + "\n").encode("utf-8")

    def decode(self, line):
        raw = _xor(base64.b64decode(line), self.key)
        return Message.from_wire(raw.decode("utf-8"))
    
##내 코덱

AES_KEY = AESGCM.generate_key(bit_length=256)


class AES256Codec(Codec):
    """AES-256-GCM 으로 메시지를 암호화하는 코덱."""

    name = "암호화(AES-256)"

    def __init__(self, key: bytes = AES_KEY):
        # AES-256은 반드시 32바이트(256비트) 열쇠가 필요하다.
        self.key = key 
        self.aesgcm = AESGCM(self.key)

    def encode(self, message):
        plaintext = message.to_wire().encode("utf-8")

        # nonce(=IV): 메시지마다 달라야 하는 "일회용 숫자". 12바이트가 표준.
        nonce = os.urandom(12)
        #메세지마다ㅏ 새로운 랜덤 12바이트 --> 암호문 앞에 붙여서 같이 보내야 decode할 때 다시 쓸 수 있음
        
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, None)
        # encrypt()가 암호문 뒤에 인증 태그까지 붙여서 돌려준다.
        # encrpyt는 평문을 암호문으로 바꾸는것이고 nonce는 1회성 계속 랜덤으로 돌림

        # decode할 때 nonce가 또 필요하므로, 앞에 붙여서 같이 보낸다.
        payload = nonce + ciphertext #12바잍 +  n바이트
        return (base64.b64encode(payload).decode("ascii") + "\n").encode("utf-8")
        #payload를 base64로 인코딩하고 아스키로 디코드한 뒤 줄바꿈하고 다시 인간언어로 인코드해서 전송
    def decode(self, line):
        payload = base64.b64decode(line)

        nonce = payload[:12]
        ciphertext = payload[12:]
        #payload = nonce + ciphertext
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, None)
        return Message.from_wire(plaintext.decode("utf-8"))