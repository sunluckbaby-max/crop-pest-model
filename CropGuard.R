project_dir <- "C:/Users/hsun/OneDrive/2_seeking for job/AI_projects/crop-pest model simplified/CropGuard"

# 创建项目文件夹（如果不存在）
dir.create(
  project_dir,
  recursive = TRUE,
  showWarnings = FALSE
)

# 创建子文件夹
dir.create(
  file.path(project_dir, "data"),
  showWarnings = FALSE
)

dir.create(
  file.path(project_dir, "output"),
  showWarnings = FALSE
)

# 切换工作目录
setwd(project_dir)


#### Module 1: generate weather in R
# 构造季节性平均温度趋势
days  = 150

# 从0开始的模拟日序号
day_index <- 0:(days - 1)

# 在季节趋势基础上加入逐日随机波动
tmean <- seasonal_temperature +
  rnorm(days, mean = 0, sd = 2)

seasonal_temperature <- 20 +
  7 * sin(2 * pi * (day_index - 30) / 180)

# 根据平均温度生成最低和最高温度
tmin <- tmean - runif(days, min = 4, max = 8)
tmax <- tmean + runif(days, min = 4, max = 8)

# 相对湿度，并限制在35%—100%
relative_humidity <- pmin(
  pmax(
    70 + rnorm(days, mean = 0, sd = 12),
    35
  ),
  100
)

# 是否发生降雨
rainfall_occurrence <- runif(days) < 0.25

## if rain, use gamma to simulate the amount of rain
rainfall_amount <- rgamma(
  days,
  shape = 2,
  scale = 5
)


rainfall_amount[rainfall_occurrence == F] = 0

rainfall= rainfall_amount

# 模拟太阳辐射，并限制在5—30 MJ/m²/day
solar_radiation <- pmin(
  pmax(
    17 +
      5 * sin(2 * pi * day_index / 180) +
      rnorm(days, mean = 0, sd = 2),
    5
  ),
  30
)

weather = data.frame(dates = seq.Date(
  from = as.Date("2026-04-01"),
  by = "day",
  length.out = 150
), tmin = tmin, tmax= tmax, relative_humidity = relative_humidity, rainfall = rainfall_amount , solar_radiation = solar_radiation)



# 3. 保存天气数据
# ------------------------------------------------------------

save_weather_data <- function(
    weather,
    file_path = "data/weather.csv"
) {
  
  write.csv(
    weather,
    file = file_path,
    row.names = FALSE
  )
  
  message(
    paste("Weather data saved to:", file_path)
  )
}



### Second: 积温与生育期模块
# ============================================================
# CropGuard - Thermal time and phenology module in R
# ============================================================


# ------------------------------------------------------------
# 1. 模型参数
# ------------------------------------------------------------

# 辣椒生长基础温度
BASE_TEMPERATURE <- 10

# 有效积温计算中的最高温度上限
MAX_EFFECTIVE_TEMPERATURE <- 35

# 辣椒不同生育期的累计积温阈值
#
# cumulative GDD < 150       Seedling
# 150 <= cumulative GDD < 450   Vegetative
# 450 <= cumulative GDD < 750   Flowering
# 750 <= cumulative GDD < 1100  Fruit development
# cumulative GDD >= 1100        Maturity


# 3. 计算每日平均温度
# ------------------------------------------------------------

phenology_results = weather
# 计算平均温度
phenology_results$tmean = (phenology_results$tmax+ phenology_results$tmin)/2
# 计算每日积温
phenology_results$daily_gdd = phenology_results$tmean - BASE_TEMPERATURE
# 计算累计积温
phenology_results$cumulative_gdd = cumsum(phenology_results$daily_gdd)
# 根据累计积温判断生育期
phenology_results$growth_stage = NA

phenology_results$growth_stage[phenology_results$cumulative_gdd<150] = "Seedling"
phenology_results$growth_stage[phenology_results$cumulative_gdd>=150 & (phenology_results$cumulative_gdd < 450)] = "Vegetative"
phenology_results$growth_stage[phenology_results$cumulative_gdd>=450 & (phenology_results$cumulative_gdd < 750)] = "Flowering"
phenology_results$growth_stage[phenology_results$cumulative_gdd>=750 & (phenology_results$cumulative_gdd < 1100)] = "Fruit development"
phenology_results$growth_stage[phenology_results$cumulative_gdd>=1100 ] = "Maturity"


# 8. visulization
### cumulative graph
plot(
  phenology_results$date,
  phenology_results$cumulative_gdd,
  type = "l",
  xlab = "Date",
  ylab = "Cumulative GDD",
  main = "Simulated cumulative growing degree days"
)
# 添加不同生育期阈值线
stage_threshold = c(
  Seedling = 150,
  Vegetative = 450,
  Flowering = 750,
  Fruit_development = 1100
)

abline(
  h = stage_threshold,
  lty = 2
)



#### third: 叶面积指数和生物量
# ============================================================
# CropGuard - LAI and biomass module in R
# ============================================================


# ------------------------------------------------------------
# 1. 模型参数
# ------------------------------------------------------------

# 最大叶面积指数
MAX_LAI <- 4.0

# Logistic曲线增长速率参数
LAI_GROWTH_RATE <- 0.008

# LAI快速增长的积温中心点
LAI_MIDPOINT_GDD <- 450

# Beer-Lambert冠层消光系数
EXTINCTION_COEFFICIENT <- 0.65

# 辐射利用效率
# 单位示例：g dry matter / MJ intercepted radiation
RADIATION_USE_EFFICIENCY <- 1.4


### calculate LAI
biomass_results = phenology_results
## 计算叶面积指数 LAI
biomass_results$lai = MAX_LAI / (1 + exp(-LAI_GROWTH_RATE*(biomass_results$cumulative_gdd - LAI_MIDPOINT_GDD)))
## 计算冠层截获辐射比例2
biomass_results$radiation_interception = 1 - exp(-EXTINCTION_COEFFICIENT*biomass_results$lai)
## 计算每日截获太阳辐射
biomass_results$intercepted_radiation = solar_radiation*biomass_results$radiation_interception
## 计算每日新增生物量
biomass_results$daily_biomass = biomass_results$intercepted_radiation*RADIATION_USE_EFFICIENCY
## 计算累计生物量
biomass_results$cumulative_biomass = cumsum(biomass_results$daily_biomass)



#绘制LAI图
plot(
  biomass_results$date,
  biomass_results$lai,
  type = "l",
  xlab = "Date",
  ylab = "Leaf Area Index",
  main = "Simulated pepper leaf area index",
  ylim = c(0, MAX_LAI)
)

#绘制累计生物量图
plot(
  biomass_results$date,
  biomass_results$cumulative_biomass,
  type = "l",
  xlab = "Date",
  ylab = "Cumulative biomass",
  main = "Simulated cumulative pepper biomass"
)

# 绘制每日新增生物量图
plot(
  biomass_results$date,
  biomass_results$daily_biomass,
  type = "l",
  xlab = "Date",
  ylab = "Daily biomass",
  main = "Simulated daily pepper biomass accumulation"
)


#### Fourth: 病害风险模块
# ============================================================
# CropGuard - Disease risk module in R
# Target disease: Pepper Phytophthora blight
# ============================================================


# ------------------------------------------------------------
# 1. 病害风险模型参数
# ------------------------------------------------------------

# 辣椒疫病发生的示范最适温度
OPTIMUM_TEMPERATURE <- 26

# 控制温度适生曲线宽度
# 数值越大，适宜温度范围越宽
TEMPERATURE_WIDTH <- 6

# 湿度适生下限
HUMIDITY_LOWER_THRESHOLD <- 60

# 接近完全适生时的湿度
HUMIDITY_UPPER_THRESHOLD <- 95

# 控制降雨适生曲线的尺度参数
RAINFALL_SCALE <- 8


# 各风险因子的权重
WEIGHT_TEMPERATURE <- 0.30
WEIGHT_HUMIDITY <- 0.30
WEIGHT_RAINFALL <- 0.25
WEIGHT_GROWTH_STAGE <- 0.15


# 风险等级阈值
RISK_MODERATE_THRESHOLD <- 0.40
RISK_HIGH_THRESHOLD <- 0.65
RISK_VERY_HIGH_THRESHOLD <- 0.80


# 不同生育期的寄主易感性
#
# 注意：
# 这些是示范值，不是经过田间试验校准的最终参数

STAGE_SUSCEPTIBILITY <- c(
  "Seedling" = 0.55,
  "Vegetative" = 0.75,
  "Flowering" = 1.00,
  "Fruit development" = 0.90,
  "Maturity" = 0.65
)


disease_risk_results = biomass_results
#### 计算温度适生性
# 当tmean接近最适温度时，适生性接近1
# 当tmean远离最适温度时，适生性逐渐下降
# 使用Gaussian响应函数
disease_risk_results$temperature_factor = exp(
  -0.5 *
    (
      (tmean - OPTIMUM_TEMPERATURE) /
        TEMPERATURE_WIDTH
    )^2
)

### 计算湿度适生性
# 低于60%时适生性设为0
# 60%—95%之间线性增加
# 高于95%时适生性设为1
disease_risk_results$humidity_factor = (
  relative_humidity -
    HUMIDITY_LOWER_THRESHOLD
) / (
  HUMIDITY_UPPER_THRESHOLD -
    HUMIDITY_LOWER_THRESHOLD
)


### 计算降雨适生性
# 饱和型函数
#
# 无降雨时为0
# 随降雨量增加而升高
# 大雨时逐渐接近1
disease_risk_results$rainfall_factor = 1 -
  exp(
    -rainfall / RAINFALL_SCALE
  )


### 获取不同生育期易感性
disease_risk_results$stage_factor = unname(STAGE_SUSCEPTIBILITY[disease_risk_results$growth_stage])



### 计算综合病害风险
disease_risk_results$disease_risk = WEIGHT_TEMPERATURE*disease_risk_results$temperature_factor + WEIGHT_HUMIDITY *disease_risk_results$humidity_factor +  WEIGHT_RAINFALL *disease_risk_results$rainfall_factor + WEIGHT_GROWTH_STAGE *disease_risk_results$stage_factor


### 将连续风险值转换为风险等级
disease_risk_results$risk_level = NA
disease_risk_results$risk_level[disease_risk_results$disease_risk < 0.40] = "Low"
disease_risk_results$risk_level[disease_risk_results$disease_risk >= 0.40 & (disease_risk_results$disease_risk < 0.65)] = "Moderate"
disease_risk_results$risk_level[disease_risk_results$disease_risk >= 0.65 & (disease_risk_results$disease_risk < 0.80)] = "High"
disease_risk_results$risk_level[disease_risk_results$disease_risk > 0.8] = "Very high"


### 生成管理建议
recommendations <- c(
  "Low" =
    "Maintain routine field monitoring.",
  
  "Moderate" =
    "Increase field inspection frequency and monitor wet areas.",
  
  "High" =
    "Inspect susceptible plots and prepare preventive management.",
  
  "Very high" =
    "Immediate field inspection and management intervention recommended."
)

disease_risk_results$recommendations = unname(recommendations[disease_risk_results$risk_level])



### 绘制每日病害风险
plot(
  disease_risk_results$date,
  disease_risk_results$disease_risk,
  type = "l",
  xlab = "Date",
  ylab = "Disease risk",
  main = "Simulated daily pepper Phytophthora blight risk",
  ylim = c(0, 1)
)

abline(
  h = c(RISK_MODERATE_THRESHOLD, RISK_HIGH_THRESHOLD, RISK_VERY_HIGH_THRESHOLD),
  lty = 2
)





