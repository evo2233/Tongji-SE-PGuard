export const refreshGap = 30*60*1000;
import axios from 'axios';
import { Storage } from '@ionic/storage';
import { backendUrl } from './config';
import { useIonRouter } from '@ionic/vue';
import { presentAlert, errorAlert } from '@/utils/alert';
const storage = new Storage();
await (await storage).create();
interface RefreshResponce{
    access_token:string
}
const TokenService = {
  async getRefreshTime() {
    return await (await storage).get('refresh_time');
  },

  async setRefreshTime(refreshTime: number) {
    await (await storage).set('refresh_time', refreshTime);
  },

  async getAccessToken() {
    return await (await storage).get('access_token');
  },

  async setAccessToken(token: string) {
    await (await storage).set('access_token', token);
  },

  async clearTokens() {
    await (await storage).remove('access_token');
    await (await storage).remove('refresh_token');
    await (await storage).remove('refresh_time');
    const ionRouter = useIonRouter();
    ionRouter.push('/login');
  },

  async refreshAccessToken() {
    const refreshToken = await (await storage).get('refresh_token');
    const oldToken = await (await storage).get('access_token');
    try {
      const response = await axios.post<RefreshResponce>(backendUrl+'/user/refresh', 
        refreshToken ,
        {
            headers: {
                Authorization: `Bearer ${oldToken}`,
            },
        }
      );
      if(response.status===200){
        const newAccessToken = response.data.access_token;
        await this.setAccessToken(newAccessToken);
        const newRefreshTime = Date.now() + refreshGap; // 当前时间 + 30分钟
        await this.setRefreshTime(newRefreshTime);
        
      }else{
        presentAlert("刷新失败","","");
        this.clearTokens();
      }
      
    } catch (error:any) {
      errorAlert(error);
      this.clearTokens();
    }
  }
};
let refreshTaskRunning = false; 

const startTokenRefreshTask = async () => {
  if (refreshTaskRunning) {
    console.log('Token refresh task is already running. Skipping new task creation.');
    return; 
  }

  refreshTaskRunning = true; // 标记任务已启动

  const checkTokenStatus = async () => {
    const refreshTime = await TokenService.getRefreshTime();
    const currentTime = Date.now();

    if (!refreshTime || refreshTime <= currentTime) {
      if(!!refreshTime){
        await TokenService.clearTokens();
      }
      refreshTaskRunning = false; // 标记任务已停止
      return;
    }

    const timeUntilRefresh = refreshTime - currentTime;

    if (timeUntilRefresh <= 30 * 1000) {
      try {
        console.log('Refreshing token...');
        await TokenService.refreshAccessToken();
        checkTokenStatus(); // 刷新后立即检查状态
      } catch (error) {
        console.error('Failed to refresh token:', error);
        await TokenService.clearTokens();
        refreshTaskRunning = false; // 标记任务已停止
        return;
      }
    } else {
      // 距离刷新时间大于30秒，设置定时器，在距离刷新时间15秒时执行
      const nextCheckDelay = Math.max(15 * 1000, timeUntilRefresh - 15 * 1000);
      console.log(`Next token check scheduled in ${nextCheckDelay / 1000} seconds.`);
      setTimeout(checkTokenStatus, nextCheckDelay);
    }
  };

  // 开始检查 token 状态
  checkTokenStatus();
  refreshTaskRunning = false; 
};

export default startTokenRefreshTask;