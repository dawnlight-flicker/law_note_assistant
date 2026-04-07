# app.py
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from data_manager import DataManager
from exporter import export_to_markdown


class LawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("法条笔记助手")
        self.root.geometry("1500x1500")

        self.data_mgr = DataManager("data.json")
        self.current_law = None
        self.current_source = None

        self.law_list = self.data_mgr.local_data and list(
            set(item['law_name'] for item in self.data_mgr.local_data)) or ["民法典"]
        self.current_law_name = tk.StringVar(value=self.law_list[0] if self.law_list else "")

        self.create_widgets()

    def create_widgets(self):
        # 顶部栏
        top_frame = tb.Frame(self.root)
        top_frame.pack(pady=15, padx=20, fill='x')

        tb.Label(top_frame, text="选择法典:", font=("微软雅黑", 12)).pack(side=LEFT, padx=5)
        self.law_combo = tb.Combobox(top_frame, textvariable=self.current_law_name,
                                     values=self.law_list, state="readonly", width=15)
        self.law_combo.pack(side=LEFT, padx=5)

        tb.Label(top_frame, text="法条编号:", font=("微软雅黑", 12)).pack(side=LEFT, padx=5)
        self.entry = tb.Entry(top_frame, width=25, font=("微软雅黑", 11))
        self.entry.pack(side=LEFT, padx=5)
        self.entry.bind('<Return>', lambda e: self.search())

        self.search_btn = tb.Button(top_frame, text="搜索", command=self.search, bootstyle=PRIMARY)
        self.search_btn.pack(side=LEFT, padx=5)

        self.export_btn = tb.Button(top_frame, text="导出笔记", command=self.export_note,
                                    bootstyle=SUCCESS, state=DISABLED)
        self.export_btn.pack(side=LEFT, padx=5)

        # 中间标签页
        self.notebook = tb.Notebook(self.root, bootstyle=DARK)
        self.notebook.pack(pady=10, padx=20, fill=BOTH, expand=True)

        self.text_tab = tb.Frame(self.notebook)
        self.notebook.add(self.text_tab, text="📜 法条原文")
        self.article_text = tk.Text(self.text_tab, wrap=tk.WORD, font=("微软雅黑", 11),
                                    bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.article_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.ji_tab = tb.Frame(self.notebook)
        self.notebook.add(self.ji_tab, text="⚖️ 司法解释")
        self.ji_text = tk.Text(self.ji_tab, wrap=tk.WORD, font=("微软雅黑", 10),
                               bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.ji_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.exam_tab = tb.Frame(self.notebook)
        self.notebook.add(self.exam_tab, text="🎯 常见考点")
        self.exam_text = tk.Text(self.exam_tab, wrap=tk.WORD, font=("微软雅黑", 10),
                                 bg="#1e1e1e", fg="#d4d4d4", insertbackground="white")
        self.exam_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 底部状态栏
        bottom_frame = tb.Frame(self.root)
        bottom_frame.pack(side=BOTTOM, fill=X, padx=10, pady=5)

        self.status_label = tb.Label(bottom_frame, text="就绪", anchor=W, bootstyle=SECONDARY)
        self.status_label.pack(side=LEFT, fill=X, expand=True)

        self.source_label = tb.Label(bottom_frame, text="", anchor=E, bootstyle=INFO)
        self.source_label.pack(side=RIGHT, padx=5)

        self.feedback_btn = tb.Button(bottom_frame, text="💬 反馈建议", command=self.show_feedback,
                                      bootstyle=INFO, width=12)
        self.feedback_btn.pack(side=RIGHT, padx=5)

    def search(self):
        keyword = self.entry.get().strip()
        if not keyword:
            messagebox.showwarning("提示", "请输入法条编号")
            return

        selected_law = self.current_law_name.get()
        results, source = self.data_mgr.search(keyword, law_name=selected_law)

        if not results:
            messagebox.showinfo("未找到", f"在《{selected_law}》中未找到编号包含“{keyword}”的法条\n（已尝试api调取）")
            self.clear_display()
            self.export_btn.config(state=DISABLED)
            self.current_law = None
            self.status_label.config(text="未找到相关法条")
            self.source_label.config(text="")
            return

        self.current_law = results[0]
        self.current_source = source
        self.display_law(self.current_law)
        self.export_btn.config(state=NORMAL)

        # 显示数据来源
        if source == 'local':
            self.source_label.config(text="✅ 数据来源：本地审核库（准确可靠）", bootstyle=SUCCESS)
        else:
            self.source_label.config(text="🌐 数据来源：api调取（仅供参考）", bootstyle=WARNING)

        self.status_label.config(
            text=f"当前显示：{self.current_law['law_name']}第{self.current_law['article_number']}条")

    def display_law(self, law):
        self.article_text.delete(1.0, tk.END)
        self.ji_text.delete(1.0, tk.END)
        self.exam_text.delete(1.0, tk.END)

        self.article_text.insert(tk.END, law.get('article_text', ''))

        if law.get('judicial_interpretations'):
            for ji in law['judicial_interpretations']:
                self.ji_text.insert(tk.END, f"【{ji['title']}】\n\n{ji['content']}\n\n{'-' * 50}\n\n")
        else:
            self.ji_text.insert(tk.END, "暂无关联司法解释")

        if law.get('exam_points'):
            for point in law['exam_points']:
                self.exam_text.insert(tk.END, f"• {point}\n\n")
        else:
            self.exam_text.insert(tk.END, "暂无考点信息")

    def clear_display(self):
        self.article_text.delete(1.0, tk.END)
        self.ji_text.delete(1.0, tk.END)
        self.exam_text.delete(1.0, tk.END)

    def export_note(self):
        if not self.current_law:
            messagebox.showwarning("提示", "没有可导出的法条")
            return
        default_name = f"{self.current_law['law_name']}第{self.current_law['article_number']}条_笔记.md"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md"), ("文本文件", "*.txt")],
            initialfile=default_name
        )
        if file_path:
            try:
                export_to_markdown(self.current_law, file_path)
                messagebox.showinfo("导出成功", f"笔记已保存到：{file_path}")
                self.status_label.config(text=f"已导出：{file_path.split('/')[-1]}")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))

    def show_feedback(self):
        messagebox.showinfo("反馈建议",
                            "感谢您的使用！\n\n如需反馈，请发送邮件至：feedback@lawtool.com（占位）\n或直接微信联系开发者。")


if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = LawApp(root)
    root.mainloop()