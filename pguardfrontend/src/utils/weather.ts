import axios from 'axios';
import storage from './storage';
import { backendUrl, weatherUrl, weatherApiKey } from './config';


// 获取当前时间的小时
interface CityCodeResponse{
    cityCode:string
}
export interface WeatherCast {
  date: string;        // 日期
  week: string;        // 星期几
  dayweather: string;  // 白天气象
  nightweather: string; // 晚上天气
  daytemp: string;     // 白天气温
  nighttemp: string;   // 晚上气温
  daywind: string;     // 白天风向
  nightwind: string;   // 晚上风向
  daypower: string;    // 白天风力
  nightpower: string;  // 晚上风力
  daytemp_float: string; // 白天气温（浮动）
  nighttemp_float: string; // 晚上气温（浮动）
}

export interface Forecast {
  city: string;        // 城市
  adcode: string;      // 城市代码
  province: string;    // 省份
  reporttime: string;  // 上次更新的时间
  casts: WeatherCast[]; // 天气预报数组
}

interface WeatherResponse {
  status: string;      // 状态码
  count: string;       // 返回的城市数
  info: string;        // 返回信息
  infocode: string;    // 返回信息码
  forecasts: Forecast[]; // 天气预报数据
}

// 获取当前时间的小时
const getCurrentHour = (): number => new Date().getHours();

// 获取用户城市代码
const getUserCityCode = async (): Promise<string | null> => {
  try {
    const token = await storage.get('access_token');
    if (!token) {
      return null;  // 如果没有 token，返回 null
    }

    const response = await axios.get<CityCodeResponse>(`${backendUrl}/user/city`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 200 && response.data.cityCode) {
      return response.data.cityCode;
    }

    return null;  // 如果没有 cityCode，返回 null
  } catch (error) {
    console.error('获取用户城市代码失败:', error);
    return null;
  }
};

// 获取天气数据并更新存储
const fetchWeatherData = async (cityCode: string): Promise<Forecast | null> => {
  try {
    const response = await axios.get<WeatherResponse>(`${weatherUrl}?key=${weatherApiKey}&city=${cityCode}&extensions=all`);

    if (response.data.status === '1' && response.data.forecasts && response.data.forecasts.length > 0) {
      const weatherData = response.data.forecasts[0];  // 获取第一个天气预报
      await storage.set('weatherData', weatherData);  // 存储天气数据
      return weatherData;  // 返回天气数据
    } else {
      return null;  // 如果返回数据格式不正确，返回 null
    }
  } catch (error) {
    console.error('获取天气数据失败:', error);
    return null;
  }
};

// 获取并返回天气数据
export const getWeather = async (): Promise<{} | Forecast> => {
    try {
      // 获取存储中的天气信息
      const storedWeatherData = await storage.get('weatherData');
      const userCityCode = await getUserCityCode();
  
      if (!userCityCode) {
        console.warn('没有获取到城市代码');
        return storedWeatherData || {};  // 如果没有获取到用户城市代码，返回存储中的数据或空对象
      }
  
      const currentHour = getCurrentHour();
  
      // 检查是否需要更新天气数据
      if (!storedWeatherData || storedWeatherData.city !== userCityCode || isWeatherDataExpired(storedWeatherData, currentHour)) {
        // 如果没有存储的天气信息，或者城市不匹配，或者天气数据已经过时
        console.log('更新天气数据');
        const newWeatherData = await fetchWeatherData(userCityCode);
        return newWeatherData || {};  // 如果没有新的天气数据，返回空对象
      }
  
      // 如果不需要更新，返回存储的天气数据
      return storedWeatherData;
    } catch (error) {
      console.error('获取天气信息失败:', error);
      return {};  // 出现错误时返回空对象
    }
  };

// 判断天气数据是否过时
const isWeatherDataExpired = (weatherData: Forecast, currentHour: number): boolean => {
  const lastUpdatedHour = new Date(weatherData.reporttime).getHours();  // 获取上次更新的小时
  return currentHour < lastUpdatedHour || currentHour >= lastUpdatedHour + 3;  // 如果距离上次更新已经超过 3 小时，认为数据过时
};