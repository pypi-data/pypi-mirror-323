# C_healthy

C_healthy là thư viện Python để tính toán các chỉ số sức khỏe (BMI, BMR, TDEE, và nhiều chỉ số khác) 

## Cách cài đặt
```bash
pip install C_healthy
```
## Cách sử dụng 
```bash
from C_healthy import BMI, BMR, TDEE, WHR, LBM, BFP, BBW, IBW, MA, FFMI, RFM, VFR, BSA, VO2MAX, HSI, MMI, BFM

bmi = BMI(70, 1.75)
bmr = BMR("nam", 60, 1.75, 18)
tdee = TDEE("nam", 60, 1.75, 18, 3)
lbm = LBM("nam", 70, 1.75) 
ffmi = FFMI("nam", 60, 1.7)
rfm = RFM(85, 1.7) 
bfp = BFP("nam", 70, 1.75, 20)
ibw = IBW("nam", 1.75)
whr = WHR("nam", 85, 95)
bbw = BBW(60)
ma = MA("nam", 70, 1.7, 18)
vfr = VFR(85, 95)
bsa = BSA(1.7, 60)
vo2max = VO2MAX(110, 60)
hsi = HSI("nam", 60, 1.7, 18, 200, 110)
mmi = MMI("nam", 60, 1.7)
bfm = BFM("nam", 60, 1.7, 18)
print("BMI:", bmi)
print("BMR:", bmr)
print("TDEE:", tdee)
print("LBM:", lbm)
print("FFMI:", ffmi)
print("RFM:", rfm)
print("BFP:", bfp)
print("IBW:", ibw)
print("WHR:", whr)
print("BBW:", bbw)
print("MA:", ma)
print("VFR:", vfr)
print("BSA:", bsa)
print("VO2MAX:", vo2max)
print("HSI:", hsi)
print("MMI:", mmi)
print("BFM:", bfm)
```

## Hoặc có thể dùng cho nhiều người bằng đoạn oop sau
```bash
import sys
from C_healthy import BMI, BMR, TDEE, WHR, LBM, BFP, NW, IBW, MA

#sys.stdin = open('TASK.inp', 'r')   # Đọc dữ liệu từ TASK.inp
#sys.stdout = open('TASK.out', 'w') # Ghi dữ liệu ra TASK.out

class BodyIndex:
    def __init__(self, gioi_tinh, chieu_cao, can_nang, tuoi, chi_so_R, vong_eo, vong_hong):
        self.gioi_tinh = gioi_tinh
        self.chieu_cao = chieu_cao
        self.can_nang = can_nang
        self.tuoi = tuoi 
        self.chi_so_R = chi_so_R
        self.vong_eo = vong_eo
        self.vong_hong = vong_hong
    def hien_thi_ket_qua(self):
        print(BMI(self.can_nang, self.chieu_cao))
        print(BMR(self.gioi_tinh, self.can_nang, self.chieu_cao, self.tuoi))
        print(TDEE(self.gioi_tinh, self.can_nang, self.chieu_cao, self.tuoi, self.chi_so_R))
        print(LBM(self.gioi_tinh, self.can_nang, self.chieu_cao))
        print(BFP(self.gioi_tinh, self.can_nang, self.chieu_cao, self.tuoi))
        print(WHR(self.gioi_tinh, self.vong_eo, self.vong_hong))
        print(IBW(self.gioi_tinh, self.chieu_cao))
        print(NW(self.can_nang))
        print(MA(self.gioi_tinh, self.can_nang, self.chieu_cao, self.tuoi))

TruongChinh = BodyIndex("nam", 1.7, 70, 18, 3, 85, 95)
TruongChinh.hien_thi_ket_qua() 
# ... Và thêm nhiều người khác ở đây
```
CUỐI CÙNG CẢM ƠN CÁC BẠN ĐÃ TIN DÙNG THƯ VIỆN CỦA MÌNH