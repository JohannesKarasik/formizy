import fitz
doc = fitz.open("YOUR_PDF.pdf")
page = doc[0]

page.insert_text((200, 300), "HELLO", fontsize=12)
doc.save("out.pdf")
