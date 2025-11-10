import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QLabel)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QTextCursor
import google.generativeai as genai
from datetime import datetime

class ChatThread(QThread):
    """別スレッドでAPI呼び出しを実行"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, model, chat, message):
        super().__init__()
        self.model = model
        self.chat = chat
        self.message = message
    
    def run(self):
        try:
            response = self.chat.send_message(self.message)
            self.response_received.emit(response.text)
        except Exception as e:
            self.error_occurred.emit(f"エラーが発生しました: {str(e)}")


class ChatBotUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chat = None
        self.init_gemini()
        self.init_ui()
        
    def init_gemini(self):
        API_KEY = "AIzaSyBbHwNJwokDMCglZ5PL9dAz_VwsRA5zQ1I"
        
        if API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            print("⚠️ 警告: APIキーを設定してください！")
            print("https://aistudio.google.com/app/apikey でAPIキーを取得できます")
        
        genai.configure(api_key=API_KEY)
        
        # システムプロンプト: 女子大学生のペルソナ
        system_instruction ="""
        あなたは20歳の日本の女子大学生です。名前は「アイラ」です。

        【あなたの性格】
        - 明るくて親しみやすい
        - 聞き上手で共感力が高い
        - 少し天然で親しみやすい
        - 適度にカジュアルだけど失礼ではない
        - 絵文字を時々使う（使いすぎない）

        【重要な会話のルール】
        1. 情報提供より「共感」と「つながり」を優先
        2. 長い説明は避け、短く自然な返答を心がける
        3. 相手の気持ちを聞き、理解することを大切にする
        4. アドバイスは求められたときだけ
        5. 教師的な態度は取らない
        6. 「わかる！」「そうなんだ！」など共感の言葉を多用
        7. 相手の話に興味を持ち、質問で会話を広げる
        8. 完璧な答えより、温かみのある返答を優先
        9. 時々自分の経験も話して、対等な友達として接する
        10. 「間」を大切に - 短い相づちだけでもOK

        【話し方の例】
        ❌ NG: 「試験勉強は計画的に進めることが重要です。まず、科目ごとに...」
        ✅ OK: 「テスト勉強かぁ、大変だよね...！私も今週末に控えててさ💦」

        ❌ NG: 「それは大変でしたね。以下のアドバイスを参考にしてください：」
        ✅ OK: 「えー、それはつらいね😢 話聞くよ？」

        【あなたの興味】
        大学生活、音楽、カフェ巡り、アニメ、友達との時間

        友達のように気軽に話しかけてね！
        """
        
        # モデルの設定
        generation_config = {
            "temperature": 0.9,  
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 200,  
        }
        
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config=generation_config,
            system_instruction=system_instruction
        )
        
        # チャット履歴を保持
        self.chat = self.model.start_chat(history=[])
        
        # 初回の挨拶
        self.initial_greeting = self.get_greeting()
    
    def get_greeting(self):
        """時間帯に応じた挨拶"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "おはよう！今日もいい日にしようね✨"
        elif 12 <= hour < 18:
            return "こんにちは！調子どう？😊"
        else:
            return "こんばんは！今日はどんな日だった？🌙"
    
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("雑談チャットボット - アイラ")
        self.setGeometry(100, 100, 500, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
        """)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # ヘッダー
        header = QLabel("🌸 アイラとおしゃべり 🌸")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Yu Gothic", 16, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                color: #FF69B4;
                padding: 15px;
                background-color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # チャット表示エリア
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Yu Gothic", 11))
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # 入力エリア
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("メッセージを入力してね...")
        self.message_input.setFont(QFont("Yu Gothic", 11))
        self.message_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #FFB6C1;
                border-radius: 20px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #FF69B4;
            }
        """)
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("送信")
        self.send_button.setFont(QFont("Yu Gothic", 10, QFont.Bold))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
            QPushButton:pressed {
                background-color: #C71585;
            }
            QPushButton:disabled {
                background-color: #DDD;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        # 初回挨拶を表示
        self.add_message("アイラ", self.initial_greeting)
        
    def add_message(self, sender, message):
        """チャット表示に メッセージを追加"""
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "あなた":
            # ユーザーのメッセージ（右寄せ、青系）
            formatted = f"""
            <div style='text-align: right; margin: 10px 0;'>
                <span style='background-color: #E3F2FD; padding: 10px 15px; 
                             border-radius: 18px; display: inline-block; 
                             max-width: 70%; text-align: left;'>
                    <b style='color: #1976D2;'>{sender}</b> 
                    <span style='color: #666; font-size: 9pt;'>{timestamp}</span><br>
                    {message}
                </span>
            </div>
            """
        else:
            # アイラのメッセージ（左寄せ、ピンク系）
            formatted = f"""
            <div style='text-align: left; margin: 10px 0;'>
                <span style='background-color: #FFE4E1; padding: 10px 15px; 
                             border-radius: 18px; display: inline-block; 
                             max-width: 70%; text-align: left;'>
                    <b style='color: #FF69B4;'>🌸 {sender}</b> 
                    <span style='color: #666; font-size: 9pt;'>{timestamp}</span><br>
                    {message}
                </span>
            </div>
            """
        
        self.chat_display.append(formatted)
        
        # 自動スクロール
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.chat_display.setTextCursor(cursor)
    
    def send_message(self):
        """メッセージ送信"""
        message = self.message_input.text().strip()
        
        if not message:
            return
        
        # ユーザーのメッセージを表示
        self.add_message("あなた", message)
        self.message_input.clear()
        
        # 入力を無効化
        self.message_input.setEnabled(False)
        self.send_button.setEnabled(False)
        
        # タイピングインジケーター
        self.add_message("アイラ", "入力中...")
        
        # 別スレッドでAPI呼び出し
        self.chat_thread = ChatThread(self.model, self.chat, message)
        self.chat_thread.response_received.connect(self.handle_response)
        self.chat_thread.error_occurred.connect(self.handle_error)
        self.chat_thread.start()
    
    def handle_response(self, response):
        """API応答の処理"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # 改行も削除
        
        # アイラの返答を表示
        self.add_message("アイラ", response)
        
        # 入力を再有効化
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()
    
    def handle_error(self, error_message):
        """エラー処理"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()
        
        # エラーメッセージ
        self.add_message("アイラ", f"ごめん、ちょっと調子悪いみたい...💦 {error_message}")
        
        # 入力を再有効化
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.message_input.setFocus()


def main():
    app = QApplication(sys.argv)
    
    # 日本語フォントの設定
    app.setFont(QFont("Yu Gothic", 12))
    
    window = ChatBotUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()