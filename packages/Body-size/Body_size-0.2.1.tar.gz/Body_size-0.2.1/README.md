# Giới Thiệu

Body_size là một thư viện dùng để xét các kích thước theo các tiêu chuẩn quốc tế (USA và UK)

##  Cách Cài Đặt

pip install Body_size

## Cách Sử Dụng

from Body_size import usa_size, uk_size, uk_chart

print(uk_size("man", 65, 170))
print(uk_size("woman", 50, 160))
print(uk_size("man", 75, 175))

print(usa_size("man", 70, 170)) 
print(usa_size("woman", 55, 160))  
print(usa_size("man", 85, 180))

print(uk_chart("woman", 75, 64, 81, 147))  
print(uk_chart("woman", 84, 66, 86, 152))  
print(uk_chart("woman", 92, 72, 91, 158))  
print(uk_chart("woman", 108, 80, 110, 168))

### Cảm ơn mọi người đã tinh tưởng sử dụng thư viện của chúng tôi.