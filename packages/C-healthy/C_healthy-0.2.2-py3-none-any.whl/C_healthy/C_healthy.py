# !py
# Author: Nguyen Truong Chinh (NTC++)
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------------------------- #

import math

# BMI (chỉ số khối cơ thể)
def BMI(can_nang, chieu_cao):
    try:
        if(can_nang > 0 and chieu_cao > 0):
            return round(can_nang / (chieu_cao ** 2), 2)
        else:
            return "Invalid input"   
    except Exception as e:
        raise ValueError(f"[{e}]")

# BMR (Tỷ lệ chuyển hóa cơ bản)
def BMR(gioi_tinh ,can_nang, chieu_cao, tuoi):
    if(not ktra_gioi_tinh(gioi_tinh)):
        return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
    try:
        if(can_nang > 0 and chieu_cao > 0 and tuoi > 0):
            chieu_cao = chieu_cao * 100
            if(gioi_tinh.lower() == "nu"):
                #BMR = 655 + (9,6 × trọng lượng tính bằng kg) + (1,8 × chiều cao tính bằng cm) – (4,7 × tuổi tính theo năm)
                return round((655 + (9.6 * can_nang) + (1.8 * chieu_cao) - (4.7 * tuoi)), 2)
            else:
                #Nam giới: BMR = 66 + (13,7 × trọng lượng tính bằng kg) + (5 × chiều cao tính bằng cm) – (6,8 × tuổi tính theo năm)
                return round((66 + (13.7 * can_nang) + (5 * chieu_cao) - (6.8 * tuoi)), 2) 
        else:
            return "Invalid input"
    except Exception as e:
        raise ValueError(f"[{e}]")
                    
# TDEE (năng lượng tiêu thụ hàng ngày)
def TDEE(gioi_tinh, can_nang, chieu_cao, tuoi, chi_so_R):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        he_so_van_dong = {
            1: 1.2,
            2: 1.375,
            3: 1.55,
            4: 1.725,
            5: 1.9
        }
        chi_so_bmr = BMR(gioi_tinh, can_nang, chieu_cao, tuoi)
        if(chi_so_R in he_so_van_dong):
            return round((chi_so_bmr * he_so_van_dong[chi_so_R]), 2)
        else:
            valid_keys = ", ".join(str(k) for k in he_so_van_dong.keys())
            raise ValueError(f"Chi so van dong khong hop le! Chon 1 trong cac gia tri: {valid_keys}")
    except Exception as e:
        raise ValueError(f"[{e}]")
    
# WHR (tỷ lệ vòng eo/hông)    
def WHR(gioi_tinh, vong_eo, vong_hong):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        if(vong_eo <= 0 or vong_hong <= 0):
            return "Invalid input"
        return round((vong_eo / vong_hong), 2)
    except Exception as e:
        raise ValueError(f"[{e}]") 

# LBM (khối lượng cơ thể không mỡ)
def LBM(gioi_tinh, can_nang, chieu_cao):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        chieu_cao = chieu_cao * 100    
        if(gioi_tinh.lower() == "nam"):
            lbm = round(((0.32810 * can_nang) + (0.33929 * chieu_cao) - 29.5336), 2)
        else:
            lbm = round(((0.29569 * can_nang) + (0.41813 * chieu_cao) - 43.2933), 2) 
        return lbm    
    except Exception as e:
        raise ValueError(f"[{e}]")

# FFMI (đo lường lượng cơ bắp)
def FFMI(gioi_tinh, can_nang, chieu_cao):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        lbm = LBM(gioi_tinh, can_nang, chieu_cao)
        ffmi = round(lbm / (chieu_cao**2), 2)
        return ffmi
    except Exception as e:
        raise ValueError(f"[{e}]")

# RFM (khối lượng mỡ tương đối)
def RFM(vong_eo, chieu_cao):
    try:
        chieu_cao = chieu_cao * 100
        rfm = round(64 - (4 * (vong_eo / chieu_cao)), 2)
        return rfm
    except Exception as e:
        raise ValueError(f"[{e}]")

# BFP (Phần trăm mỡ cơ thể)
def BFP(gioi_tinh, can_nang, chieu_cao, tuoi):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bmi = BMI(can_nang, chieu_cao) 
        if(gioi_tinh.lower() == "nam"):
            bfp = round((1.20 * bmi) + (0.23 * tuoi) - 16.2, 2)
        else:
            bfp = round((1.20 * bmi) + (0.23 * tuoi) - 5.4, 2)
        return bfp
    except Exception as e:
        raise ValueError(f"[{e}]")

# BBW (lượng nước cần thiết mỗi ngày tính theo lít)
def BBW(can_nang):
    try:
        luong_nuoc = round(can_nang * 0.033, 2)
        return luong_nuoc
    except Exception as e:
        raise ValueError(f"[{e}]")

# IBW (cân nặng lý tưởng dựa trên chiều cao)
def IBW(gioi_tinh, chieu_cao):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        chieu_cao = chieu_cao * 100
        if(gioi_tinh.lower() == "nam"):
            ibw = round(50 + 2.3 * (chieu_cao - 152.4) / 2.54, 2)
        else:
            ibw = round(45.5 + 2.3 * (chieu_cao - 152.4) / 2.54, 2)
        return ibw
    except Exception as e:
        raise ValueError(f"[{e}]")

# MA (Metabolic age (tuổi sinh học))
def MA(gioi_tinh, can_nang, chieu_cao, tuoi):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bmr = BMR(gioi_tinh, can_nang, chieu_cao, tuoi)
        bmr_tb_nam = {
            (18, 30): 1900,
            (31, 50): 1800,
            (51, 70): 1700,
            (71, 150): 1600
        }
        bmr_tb_nu = {
            (18, 30): 1500,
            (31, 50): 1400,
            (51, 70): 1300,
            (71, 150): 1200
        }
        bang_bmr = bmr_tb_nam if gioi_tinh.lower() == "nam" else bmr_tb_nu
        bmr_tb = None
        for gioi_han_tuoi, tb_bmr in bang_bmr.items():
            if(gioi_han_tuoi[0] <= tuoi <= gioi_han_tuoi[1]):
                bmr_tb = tb_bmr
                break
        if bmr_tb is None:
            return(f"Tuoi '{tuoi}' khong duoc ho tro !") 
        he_so_dieu_chinh = (bmr - bmr_tb) / 100  
        ma = int(round(tuoi - he_so_dieu_chinh))  
        return ma
    except Exception as e:
        raise ValueError(f"[{e}]")

# VFR (đánh giá mỡ nội tạng)
def VFR(vong_eo, vong_hong):
    try:
        vfr = round(vong_eo / vong_hong, 2)
        return vfr
    except Exception as e:
        raise ValueError(f"[{e}]")

# BSA (diện tích bề mặt cơ thể)
def BSA(chieu_cao, can_nang):
    try: 
        chieu_cao = chieu_cao * 100
        bsa = round(math.sqrt((chieu_cao * can_nang) / 3600), 2)
        return bsa 
    except Exception as e:
        raise ValueError(f"[{e}]")

# VO2MAX (khả năng hấp thụ oxy tối đa)
def VO2MAX(nhip_tim_toi_da, nhip_tim_nghi):
    try:
        Vo2max = 15 * (nhip_tim_toi_da / nhip_tim_nghi)
        return Vo2max            
    except Exception as e:
        raise ValueError(f"[{e}]")

# HSI (tỷ số sức khỏe tổng thể)
def HSI(gioi_tinh, can_nang, chieu_cao, tuoi, cholesterol, huyet_ap):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bmi = BMI(can_nang, chieu_cao)
        bfp = BFP(gioi_tinh, can_nang, chieu_cao, tuoi)
        hsi = round((bmi * 0.4 + bfp * 0.3 + huyet_ap * 0.2 + cholesterol * 0.1) / 4, 2)
        return hsi 
    except Exception as e:
        raise ValueError(f"[{e}]")     

# MMI (chỉ số khối cơ bắp)
def MMI(gioi_tinh, can_nang, chieu_cao):
    try:
        ffmi = FFMI(gioi_tinh, can_nang, chieu_cao)
        mmi = round(ffmi / can_nang, 2)
        return mmi 
    except Exception as e:
        raise ValueError(f"[{e}]")

# BFM (chỉ số lượng mỡ cơ thể)
def BFM(gioi_tinh, can_nang, chieu_cao, tuoi):
    try:
        if(not ktra_gioi_tinh(gioi_tinh)):
            return("Gioi tinh cho phep: ['nam', 'nu']\nVui long nhap lai cu phap")
        bfp = BFP(gioi_tinh, can_nang, chieu_cao, tuoi)
        bfm = round(can_nang * (bfp / 100), 2)
        return bfm 
    except Exception as e:
        raise ValueError(f"[{e}]")                   

# KIỂM TRA GIỚI TÍNH         
def ktra_gioi_tinh(gioi_tinh):
    gioi_tinh_cho_phep = ["nam", "nu"]
    if isinstance(gioi_tinh, (int, float, complex)):  
        return False
    if gioi_tinh.lower() not in gioi_tinh_cho_phep:
        return False
    else: 
        return True      

# HƯỚNG DẪN SỬ DỤNG
# HƯỚNG DẪN SỬ DỤNG CHO TẤT CẢ CÁC HÀM
def HDSD(Loai):
    try:
        if(Loai.upper() == "BMI"):
            noi_dung = (
                """Lenh BMI: nhap theo cu phap BMI([can nang] [chieu cao]),
                Vi du: BMI(60, 1.75)"""
            )
        elif(Loai.upper() == "BMR"):
            noi_dung = ( 
                """Lenh BMR: nhap theo cu phap BMR([gioi tinh] [can nang], [chieu cao], [tuoi]),
                Vi du: BMR('nam', 70, 1.75, 25)"""
            )
        elif(Loai.upper() == "TDEE"):
            noi_dung = (
                """Lenh TDEE: nhap theo cu phap TDEE([gioi tinh] [can nang], [chieu cao], [tuoi], [chi so van dong]),
                Vi du: TDEE('nam', 70, 1.75, 25, 3)"""
            )
        elif(Loai.upper() == "WHR"):
            noi_dung = (
                """Lenh WHR: nhap theo cu phap WHR([gioi tinh] [vong eo] [vong hong]),
                Vi du: WHR('nu', 70, 90)"""
            )
        elif(Loai.upper() == "LBM"):
            noi_dung = (
                """Lenh LBM: nhap theo cu phap LBM([gioi tinh] [can nang] [chieu cao]),
                Vi du: LBM('nam', 70, 1.75)"""
            )
        elif(Loai.upper() == "FFMI"):
            noi_dung = (
                """Lenh FFMI: nhap theo cu phap FFMI([gioi tinh] [can nang] [chieu cao]),
                Vi du: FFMI('nam', 70, 1.75)"""
            )
        elif(Loai.upper() == "RFM"):
            noi_dung = (
                """Lenh RFM: nhap theo cu phap RFM([vong eo] [chieu cao]),
                Vi du: RFM(70, 1.75)"""
            )
        elif(Loai.upper() == "BFP"):
            noi_dung = (
                """Lenh BFP: nhap theo cu phap BFP([gioi tinh] [can nang] [chieu cao] [tuoi]),
                Vi du: BFP('nam', 70, 1.75, 25)"""
            )
        elif(Loai.upper() == "BBW"):
            noi_dung = (
                """Lenh BBW: nhap theo cu phap BBW([can nang]),
                Vi du: BBW(70)"""
            )
        elif(Loai.upper() == "IBW"):
            noi_dung = (
                """Lenh IBW: nhap theo cu phap IBW([gioi tinh] [chieu cao]),
                Vi du: IBW('nam', 1.75)"""
            )
        elif(Loai.upper() == "MA"):
            noi_dung = (
                """Lenh MA: nhap theo cu phap MA([gioi tinh] [can nang] [chieu cao] [tuoi]),
                Vi du: MA('nam', 70, 1.75, 25)"""
            )
        elif(Loai.upper() == "VFR"):
            noi_dung = (
                """Lenh VFR: nhap theo cu phap VFR([vong eo] [vong hong]),
                Vi du: VFR(70, 90)"""
            )
        elif(Loai.upper() == "BSA"):
            noi_dung = (
                """Lenh BSA: nhap theo cu phap BSA([chieu cao] [can nang]),
                Vi du: BSA(1.75, 70)"""
            )
        elif(Loai.upper() == "VO2MAX"):
            noi_dung = (
                """Lenh VO2MAX: nhap theo cu phap VO2MAX([nhip tim toi da] [nhip tim nghi]),
                Vi du: VO2MAX(200, 70)"""
            )
        elif(Loai.upper() == "HSI"):
            noi_dung = (
                """Lenh HSI: nhap theo cu phap HSI([gioi tinh] [can nang] [chieu cao] [tuoi] [cholesterol] [huyet ap]),
                Vi du: HSI('nam', 70, 1.75, 25, 200, 120)"""
            )
        elif(Loai.upper() == "MMI"):
            noi_dung = (
                """Lenh MMI: nhap theo cu phap MMI([khoi luong co bap] [can nang]),
                Vi du: MMI(30, 70)"""
            )
        elif(Loai.upper() == "BFM"):
            noi_dung = (
                """Lenh BFM: nhap theo cu phap BFM([gioi tinh] [can nang] [chieu cao] [tuoi]),
                Vi du: BFM('nam', 70, 1.75, 25)"""
            )
        elif(Loai.upper() == "ALL"):
            noi_dung = (
                """Hướng dẫn sử dụng các hàm tính toán:

1. **BMI**: Nhập theo cú pháp BMI([cân nặng] [chiều cao]).
Ví dụ: BMI(60, 1.75)

2. **BMR**: Nhập theo cú pháp BMR([giới tính] [cân nặng], [chiều cao], [tuổi]).
   Ví dụ: BMR('nam', 70, 1.75, 25)

3. **TDEE**: Nhập theo cú pháp TDEE([giới tính] [cân nặng], [chiều cao], [tuổi], [chỉ số vận động]).
   Ví dụ: TDEE('nam', 70, 1.75, 25, 3)

4. **WHR**: Nhập theo cú pháp WHR([giới tính] [vòng eo] [vòng hông]).
   Ví dụ: WHR('nữ', 70, 90)

5. **LBM**: Nhập theo cú pháp LBM([giới tính] [cân nặng] [chiều cao]).
   Ví dụ: LBM('nam', 70, 1.75)

6. **FFMI**: Nhập theo cú pháp FFMI([giới tính] [cân nặng] [chiều cao]).
   Ví dụ: FFMI('nam', 70, 1.75)

7. **RFM**: Nhập theo cú pháp RFM([vòng eo] [chiều cao]).
   Ví dụ: RFM(70, 1.75)

8. **BFP**: Nhập theo cú pháp BFP([giới tính] [cân nặng] [chiều cao] [tuổi]).
   Ví dụ: BFP('nam', 70, 1.75, 25)

9. **BBW**: Nhập theo cú pháp BBW([cân nặng]).
   Ví dụ: BBW(70)

10. **IBW**: Nhập theo cú pháp IBW([giới tính] [chiều cao]).
    Ví dụ: IBW('nam', 1.75)

11. **MA**: Nhập theo cú pháp MA([giới tính] [cân nặng] [chiều cao] [tuổi]).
    Ví dụ: MA('nam', 70, 1.75, 25)

12. **VFR**: Nhập theo cú pháp VFR([vòng eo] [vòng hông]).
    Ví dụ: VFR(70, 90)

13. **BSA**: Nhập theo cú pháp BSA([chiều cao] [cân nặng]).
    Ví dụ: BSA(1.75, 70)

14. **VO2MAX**: Nhập theo cú pháp VO2MAX([nhịp tim tối đa] [nhịp tim nghỉ]).
    Ví dụ: VO2MAX(200, 70)

15. **HSI**: Nhập theo cú pháp HSI([giới tính] [cân nặng] [chiều cao] [tuổi] [cholesterol] [huyết áp]).
    Ví dụ: HSI('nam', 70, 1.75, 25, 200, 120)

16. **MMI**: Nhập theo cú pháp MMI([khối lượng cơ bắp] [cân nặng]).
    Ví dụ: MMI(30, 70)

17. **BFM**: Nhập theo cú pháp BFM([giới tính] [cân nặng] [chiều cao] [tuổi]).
    Ví dụ: BFM('nam', 70, 1.75, 25)"""
            )    
        else:
            return "Invalid input" 
        return noi_dung 
    except Exception as e:
        raise ValueError(f"[{e}]")

# ---------------------------------------------------- Copyright by NTC++ 24/01/2025 ---------------------------------------------------- #
# THE END 