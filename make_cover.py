from PIL import Image, ImageDraw, ImageFont
W, H = 1200, 630
img = Image.new("RGB", (W, H), "#0f172a")
d = ImageDraw.Draw(img)
d.rectangle([0,0,W,140], fill="#facc15")
d.rectangle([0,H-30,W,H], fill="#facc15")
try:
    f1 = ImageFont.truetype("arial.ttf", 64)
    f2 = ImageFont.truetype("arial.ttf", 30)
    f3 = ImageFont.truetype("arial.ttf", 24)
except:
    f1 = f2 = f3 = ImageFont.load_default()
d.text((50,30), "TELECOM CHURN ANALYTICS", fill="#0f172a", font=f1)
d.text((50,220), "Power BI + Python ML", fill="#facc15", font=f2)
d.text((50,270), "5000 customers  |  133k rows  |  7 tables  |  71% accuracy", fill="white", font=f3)
d.text((50,320), "Churn prediction + dashboard + DAX + full guide", fill="#cbd5e1", font=f3)
d.text((50,420), "by Mohamed Rashwan", fill="white", font=f2)
d.text((50,470), "Python  |  Power BI  |  RandomForest  |  DAX", fill="#94a3b8", font=f3)
# simple chart bars
for i, h in enumerate([120,180,90,220,150,260,190]):
    x = 820+i*45
    d.rectangle([x, 500-h, x+30, 500], fill="#facc15" if i%2==0 else "#38bdf8")
img.save("cover.png")
print("cover saved")
