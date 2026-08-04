from pathlib import Path  #从 pathlib 这个库里面，把 Path 这个工具拿出来。
import os
import numpy as np    ## 数值计算工具库  导入 numpy 这个库，并把它简称为 np
import pandas as pd   ## 数据表(DataFrame)
import matplotlib.pyplot as plt 

### set the path to the data folder
project_dir = Path( r"C:\Users\hsun\OneDrive\2_seeking for job\AI_projects"
                    r"\crop-pest model simplified\CropGuard")
### r: 这个字符串里的反斜杠 \ 按普通字符处理，不要当作转义符。
project_dir.mkdir(parents=True, exist_ok=True)
## create data folder
data_dir = project_dir / "data"
data_dir.mkdir(parents=True, exist_ok=True) 

## 相当于R中的setwd(project_dir)
os.chdir(project_dir)  ## change the working directory to project_dir

print("Current working directory:")
print(Path.cwd())  ## print the current working directory



# Module 1: Generate weather data
## number of simulated days:
days = 150
## day index starting from 0
day_index = np.arange(days)   ## for R: day_index <- 0:(days - 1)
## seasonal mean temperature (°C) trend
seasonal_temperature = 20 + 7 * np.sin(2 * np.pi * (day_index-30) / 180)  ## np is pi, np.sin is sine function, np.pi is π


print("First 10 day indices:")
print(day_index[:10])

print("\nFirst 10 seasonal mean temperatures:") 
print(seasonal_temperature[:10])

## generate the daily mean temperature
rng = np.random.default_rng(seed=42)  ## set the random seed for reproducibility
tmean = (seasonal_temperature + rng.normal(loc=0, scale=2, size=days))  ## add random noise to the seasonal mean temperature loc: mean scale: standard deviation 
print("\ntmean:")
print(tmean[:10])

# 根据平均温度生成最低和最高温度
tmin = tmean - rng.uniform(4, 8, size=days)  ## generate daily minimum temperature
tmax = tmean + rng.uniform(4, 8, size=days)    
print("\ntmin:")
print(tmin[:10])    
print("\ntmax:")
print(tmax[:10])


# 相对湿度，并限制在35%—100%
humidity  = 70 + rng.uniform(0, 12, size=days)
relative_humidity = np.clip(humidity, 35, 100)  ## clip the values to be between 35 and 100

print("\nrelative_humidity:")
print(relative_humidity[:10])   

# 是否发生降雨
rainfall_occurrence = rng.uniform(0, 1, size=days) < 0.25  ## 25% chance of rain
print("\nrainfall:") 
print(rainfall_occurrence[:10])

## if rain, use gamma to simulate the amount of rain
rainfall_amount = rng.gamma(shape=2, scale=5, size=days)   ## gamma  distribution for rainfall amount

print("\nrainfall_amount:")
print(rainfall_amount[:10]) 

### if no rain, set rainfall amount to 0
rainfall_amount[~rainfall_occurrence] = 0  ## set rainfall amount to 0 if no rain
print("\nrainfall_amount after setting no rain days to 0:") 
print(rainfall_amount[:10])

rainfall = rainfall_amount  ## rename rainfall_amount to rainfall

# 模拟太阳辐射，并限制在5—30 MJ/m²/day
solar = 17 + 5 * np.sin(2 * np.pi * (day_index) / 180) + rng.normal(loc=0, scale=2, size=days)

solar_radiation = np.clip(solar, 5, 30)  ## clip the values to be between 5 and 30
print("\nsolar_radiation:")
print(solar_radiation[:10])

dates = pd.date_range(start="2026-04-01", periods=days,freq='D')  ## generate a date range starting from 2023-01-01 for the number of days
weather = pd.DataFrame({
    "date": dates,
    #"tmean": tmean,
    "tmin": tmin,
    "tmax": tmax,
    "relative_humidity": relative_humidity,
    "rainfall": rainfall,
    "solar_radiation": solar_radiation
})

print("\nFirst 10 rows of the generated weather data:")
print(weather.head(10))

#### 3. save weather data to CSV
## define the output path for the weather data CSV file
weather_file = data_dir / "weather_data.csv" ## define the output path for the weather data CSV file
weather.to_csv(weather_file, index=False)
print(f"\nWeather data saved to {weather_file}")
print("\nWeather data saved to")
print(weather_file)

### Second: 积温与生育期模块
# ============================================================
# CropGuard - Thermal time and phenology module in R
# ============================================================


# ------------------------------------------------------------
# 1. 模型参数
# ------------------------------------------------------------

# 辣椒生长基础温度
BASE_TEMPERATURE = 10  # °C 
# 有效积温计算中的最高温度上限
MAX_EFFECTIVE_TEMPERATURE = 35  # °C

# 辣椒不同生育期的累计积温阈值
#
# cumulative GDD < 150       Seedling
# 150 <= cumulative GDD < 450   Vegetative
# 450 <= cumulative GDD < 750   Flowering
# 750 <= cumulative GDD < 1100  Fruit development
# cumulative GDD >= 1100        Maturity

# 3. 计算每日平均温度
phenology_results = weather.copy()  ## create a copy of the weather DataFrame to store phenology results
print("\nFirst 10 rows of the phenology results DataFrame:")
print(phenology_results.head(10))

## add new columns for daily mean temperature, effective temperature, cumulative GDD, and phenological stage
## calculate daily mean temperature as the average of tmin and tmax
phenology_results["tmean"] = (phenology_results["tmin"] + phenology_results["tmax"]) / 2
## daily effective temperature calculation
phenology_results["effective_temperature"] = np.clip(
    phenology_results["tmean"],
    BASE_TEMPERATURE,
    MAX_EFFECTIVE_TEMPERATURE,
)
## daily cumulative GDD (Growing Degree Days) calculation
phenology_results["daily_gdd"] = phenology_results["effective_temperature"] - BASE_TEMPERATURE
# 计算累计积温
phenology_results["cumulative_gdd"] = phenology_results["daily_gdd"].cumsum()
# 根据累计积温判断生育期
def determine_phenological_stage(cumulative_gdd):
    if cumulative_gdd < 150:
        return "Seedling"
    elif 150 <= cumulative_gdd < 450:
        return "Vegetative"
    elif 450 <= cumulative_gdd < 750:
        return "Flowering"
    elif 750 <= cumulative_gdd < 1100:
        return "Fruit development"
    else:
        return "Maturity"

phenology_results["growth_stage"] = phenology_results["cumulative_gdd"].apply(determine_phenological_stage)
print("\nFirst 10 rows of the phenology results DataFrame:")
print(phenology_results.head(10))

### visualize the phenology results
stage_threshold = {
    "Seedling": 150,
    "Vegetative": 450,
    "Flowering": 750,
    "Fruit development": 1100
}   ### Dictionary
print("\nStage thresholds:")
print(stage_threshold)

# Plot cumulative growing degree days
plt.figure(figsize=(10, 6))
plt.plot(phenology_results["date"], phenology_results["cumulative_gdd"], label="Cumulative GDD")
# 添加生育期阈值线
for stage, threshold in stage_threshold.items():
    plt.axhline(y=threshold, linestyle='--', label=f"{stage} threshold")
print("\nStage thresholds:")
print(stage_threshold)

plt.title("Cumulative Growing Degree Days (GDD) and Phenological Stages")
plt.xlabel("Date")
plt.ylabel("Cumulative Growing Degree Days")
plt.legend()
plt.tight_layout() #    
pehnology_plot_file = data_dir / "phenology_plot.png"  ## define the output path for the phenology plot
plt.savefig(pehnology_plot_file)  ## save the plot to a file
plt.show()  #
plt.close()

#### third: 叶面积指数和生物量
# ============================================================
# CropGuard - LAI and biomass module in R
# ============================================================


# ------------------------------------------------------------
# 1. 模型参数
# ------------------------------------------------------------
# 最大叶面积指数
MAX_LAI = 4.0   

# Logistic曲线增长速率参数
LAI_GROWTH_RATE = 0.008

# LAI快速增长的积温中心点
LAI_MIDPOINT_GDD = 450

# Beer-Lambert冠层消光系数
EXTINCTION_COEFFICIENT = 0.65

# 辐射利用效率
# 单位示例：g dry matter / MJ intercepted radiation
RADIATION_USE_EFFICIENCY = 1.4

# 3. 计算叶面积指数 (LAI) 和生物量
biomass_results = phenology_results.copy()  ## create a copy of the phen
## 计算叶面积指数 LAI
biomass_results["lai"] = MAX_LAI / (1 + np.exp(-LAI_GROWTH_RATE * (biomass_results["cumulative_gdd"] - LAI_MIDPOINT_GDD)))
## 计算冠层截获辐射比例
biomass_results["radiation_interception"] = 1 - np.exp(-EXTINCTION_COEFFICIENT * biomass_results["lai"])
## 计算每日截获太阳辐射
biomass_results["intercepted_radiation"] = (
    biomass_results["solar_radiation"]
    * biomass_results["radiation_interception"]
)
## 计算每日新增生物量
biomass_results["daily_biomass"] = biomass_results["intercepted_radiation"] * RADIATION_USE_EFFICIENCY
## 计算累计生物量
biomass_results["cumulative_biomass"] = biomass_results["daily_biomass"].cumsum()
print("\nFirst 10 rows of the biomass results DataFrame:")
print(biomass_results.head(10))

### visualize the LAI and biomass results
plt.figure(figsize=(10, 6))
plt.plot(biomass_results["date"], biomass_results["lai"], label="Leaf Area Index (LAI)", color='green')
plt.title("Leaf Area Index (LAI) Over Time")    
plt.xlabel("Date")  
plt.ylabel("Leaf Area Index (LAI)")
plt.legend()    
plt.tight_layout()
lai_plot_file = data_dir / "lai_plot.png"  ## define the output path for the LAI plot
plt.savefig(lai_plot_file)  ## save the plot to a file      
plt.show()  ## show the plot    
plt.close()  ## close the plot to free memory



#### Fourth: 病害风险模块
# ============================================================
# CropGuard - Disease risk module in R
# Target disease: Pepper Phytophthora blight
# ============================================================


# ------------------------------------------------------------
# 1. 病害风险模型参数
# ------------------------------------------------------------

# 辣椒疫病发生的示范最适温度
OPTIMUM_TEMPERATURE = 26     # °C
# 控制温度适生曲线宽度
# 数值越大，适宜温度范围越宽
TEMPERATURE_WIDTH = 6          # °C
# 湿度适生下限
HUMIDITY_LOWER_THRESHOLD = 60      # %
# 湿度适生上限  
HUMIDITY_UPPER_THRESHOLD = 95     # %

# 控制降雨适生曲线的尺度参数
RAINFALL_SCALE  = 8  # mm

# 各风险因子的权重
WEIGHT_TEMPERATURE = 0.35
WEIGHT_HUMIDITY = 0.30
WEIGHT_RAINFALL = 0.25
WEIGHT_GROWTH_STAGE = 0.15

# 风险等级阈值
RISK_MODERATE_THRESHOLD = 0.40
RISK_HIGH_THRESHOLD = 0.65
RISK_VERY_HIGH_THRESHOLD = 0.80

# 不同生育期的寄主易感性
#
# 注意：
# 这些是示范值，不是经过田间试验校准的最终参数
STAGE_SUSCEPTIBILITY = {
    "Seedling": 0.55,
    "Vegetative": 0.75,
    "Flowering": 1,   
    "Fruit development": 0.90,
    "Maturity": 0.65 
}

disease_risk_results = biomass_results.copy()  ## create a copy of the biomass results DataFrame to store disease risk results  
#### 计算温度适生性
# 当tmean接近最适温度时，适生性接近1
# 当tmean远离最适温度时，适生性逐渐下降
# 使用Gaussian响应函数
disease_risk_results["temperature_factor"] = np.exp(
    -0.5 * ((disease_risk_results["tmean"] - OPTIMUM_TEMPERATURE) / TEMPERATURE_WIDTH) ** 2
)


### 计算湿度适生性
# 低于60%时适生性设为0
# 60%—95%之间线性增加
# 高于95%时适生性设为1
disease_risk_results["humidity_factor"] = (disease_risk_results["relative_humidity"]-HUMIDITY_LOWER_THRESHOLD)/(HUMIDITY_UPPER_THRESHOLD-HUMIDITY_LOWER_THRESHOLD)

### 计算降雨适生性
# 饱和型函数
#
# 无降雨时为0
# 随降雨量增加而升高
# 大雨时逐渐接近1
disease_risk_results["rainfall_factor"] = 1 - np.exp(- disease_risk_results["rainfall"] / RAINFALL_SCALE)

### 获取不同生育期易感性
disease_risk_results["stage_factor"] = disease_risk_results["growth_stage"].map(STAGE_SUSCEPTIBILITY)

### 计算综合病害风险指数
disease_risk_results["disease_risk_index"] = WEIGHT_TEMPERATURE*disease_risk_results["temperature_factor"] + WEIGHT_HUMIDITY*disease_risk_results["humidity_factor"] + WEIGHT_RAINFALL*disease_risk_results["rainfall_factor"] +   WEIGHT_GROWTH_STAGE*disease_risk_results["stage_factor"]


### 将连续风险值转换为风险等级
def determine_risk_level(risk_level):
    if risk_level < RISK_MODERATE_THRESHOLD:
        return "Low"
    elif RISK_MODERATE_THRESHOLD <= risk_level < RISK_HIGH_THRESHOLD:
        return "Moderate"
    elif RISK_HIGH_THRESHOLD <= risk_level < RISK_VERY_HIGH_THRESHOLD:
        return "High"
    else:
        return "Very High"  

disease_risk_results["risk_level"] = disease_risk_results["disease_risk_index"].apply(determine_risk_level)
print("\nFirst 10 rows of the disease risk results DataFrame:") 
print(disease_risk_results.head(10))

### 生成管理建议
recommendations = []
for index, row in disease_risk_results.iterrows():  
    if row["risk_level"] == "Low":
        recommendations.append("No immediate action needed.")
    elif row["risk_level"] == "Moderate":
        recommendations.append("Monitor the crop closely and consider preventive measures.")
    elif row["risk_level"] == "High":
        recommendations.append("Implement disease management strategies promptly.")
    else:  # Very High
        recommendations.append("Immediate intervention required to prevent severe outbreak.")           

disease_risk_results["management_recommendation"] = recommendations
print("\nFirst 10 rows of the disease risk results DataFrame with management recommendations:")     
print(disease_risk_results.head(10))


### 绘制每日病害风险
plt.figure(figsize=(10, 6))
plt.plot(disease_risk_results["date"], disease_risk_results["disease_risk_index"], label="Disease Risk Index", color='red')
# 添加风险等级阈值线    
plt.axhline(y=RISK_MODERATE_THRESHOLD, linestyle='--', color='orange', label="Moderate Risk")
plt.axhline(y=RISK_HIGH_THRESHOLD, linestyle='--', color='yellow', label="High Risk")
plt.axhline(y=RISK_VERY_HIGH_THRESHOLD, linestyle='--', color='red', label="Very High Risk")
plt.title("Disease Risk Index Over Time")
plt.xlabel("Date")
plt.ylabel("Disease Risk Index")
plt.legend()
plt.tight_layout()
disease_risk_plot_file = data_dir / "disease_risk_plot.png"
plt.savefig(disease_risk_plot_file)
plt.show()
plt.close()