<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <!-- 用户信息区域 -->
      <ion-card>
        <ion-card-header>
          <ion-card-title>用户信息</ion-card-title>
        </ion-card-header>
        <ion-card-content>
          <ion-item>
            <ion-icon slot="start" :icon="personCircleOutline" ></ion-icon>
            <ion-label>{{ username }}</ion-label>
          </ion-item>
          <ion-item>
            <ion-icon slot="start" :icon="locationOutline"></ion-icon>
            <ion-label>所在地: {{ location }}</ion-label>
          </ion-item>
          <ion-item>
            <ion-icon slot="start" :icon="timeOutline"></ion-icon>
            <ion-label>剩余使用次数: {{ sumCount }}</ion-label>
          </ion-item>
        </ion-card-content>
      </ion-card>

      <!-- 操作按钮 -->
      <ion-card>
        <ion-card-content>
          <ion-button expand="block" color="primary" @click="fetchSummary">
            总结
          </ion-button>
          <ion-button expand="block" color="secondary" @click="openRechargeModal">
            套餐充值
          </ion-button>
          <ion-button expand="block" color="tertiary" @click="openUpdateUserModal">
            更改用户信息
          </ion-button>
          <ion-button expand="block" color="danger" @click="logout">
            退出登录
          </ion-button>
        </ion-card-content>
      </ion-card>
    </ion-content>

    <!-- 修改用户信息模态框 -->
    <ion-modal :is-open="isUpdateModalOpen" @ionModalDidDismiss="closeModal">
      <ion-header>
        <ion-toolbar>
          <ion-title>修改用户信息</ion-title>
          <ion-buttons slot="start">
            <ion-button @click="closeModal">关闭</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content>
        <ion-list>
          <ion-item>
            <ion-label position="stacked">用户名</ion-label>
            <ion-input v-model="updatedUserName"></ion-input>
          </ion-item>
          <ion-item>
            <ion-label position="stacked">密码</ion-label>
            <ion-input type="password" v-model="updatedPassword">
              <ion-input-password-toggle slot="end"></ion-input-password-toggle>
            </ion-input>
          </ion-item>
          <ion-item>
            <ion-label position="stacked">重复密码</ion-label>
            <ion-input type="password" v-model="repeatPassword">
              <ion-input-password-toggle slot="end"></ion-input-password-toggle>
            </ion-input>
          </ion-item>
          <ion-item>
            <ion-input
              v-model="searchKeyword"
              type="text"
              placeholder="输入城市名搜索"
              @ionInput="onSearch"
            ></ion-input>
            <ion-select v-if="cityOptions.length" placeholder="选择城市" @ionChange="onCitySelect">
              <ion-select-option v-for="city in cityOptions" :key="city.cityCode" :value="city.cityName">
                {{ city.cityName }}
              </ion-select-option>
            </ion-select>
          </ion-item>
        </ion-list>
        <ion-button expand="block" color="success" @click="updateUserInfo">提交</ion-button>
      </ion-content>
    </ion-modal>

    <!-- 套餐充值模态框 -->
    <ion-modal ref="rechargeModal" :is-open="isRechargeModalOpen">
      <ion-header>
        <ion-toolbar>
          <ion-title>选择套餐</ion-title>
          <ion-buttons slot="start">
            <ion-button @click="closeRechargeModal">关闭</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>
      <ion-content>
        <ion-list>
          <ion-radio-group v-model="selectedPackageId">
            <ion-item v-for="pkg in packages" :key="pkg.packageId">
              <ion-label>
                {{ pkg.packageName }} 
                (价格: {{ pkg.price }}元 | 次数: {{ pkg.sumNum }})
              </ion-label>
              <ion-radio slot="start" :value="pkg.packageId"></ion-radio>
            </ion-item>
          </ion-radio-group>
        </ion-list>
        <ion-button expand="block" color="primary" @click="confirmPayment">支付</ion-button>
      </ion-content>
    </ion-modal>

    <!-- 总结模态框 -->
    <ion-modal :is-open="isSummaryModalOpen" @ionModalDidPresent="onModalDidPresent" @ionModalDidDismiss="closeSummaryModal">
      <ion-header>
        <ion-toolbar>
          <ion-title>总结</ion-title>
          <ion-buttons slot="start">
            <ion-button color="danger" @click="closeSummaryModal">关闭</ion-button>
          </ion-buttons>
        </ion-toolbar>
      </ion-header>

      <ion-content>
        <div v-if="summaryData">
          <!-- 地块总数 -->
          <ion-card>
            <ion-card-header>
              <ion-card-title>地块总数</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <ion-text color="primary">{{ summaryData.plot_count }}</ion-text>
            </ion-card-content>
          </ion-card>

          <!-- 各植物地块统计 -->
          <ion-card v-if="summaryData.plant_plot_count && Object.keys(summaryData.plant_plot_count).length">
            <ion-card-header>
              <ion-card-title>各植物地块统计</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <ion-list>
                <ion-item v-for="(count, plant) in summaryData.plant_plot_count" :key="plant">
                  <ion-icon slot="start" :icon="leafOutline"></ion-icon>
                  {{ plant }}: {{ count }}
                </ion-item>
              </ion-list>
            </ion-card-content>
          </ion-card>

          <!-- 每月病害数量 -->
          <ion-card>
            <ion-card-header>
              <ion-card-title>每月病害数量</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <canvas id="monthlyDiseaseChart" width="400" height="200"></canvas>
            </ion-card-content>
          </ion-card>

          <!-- 植物病害统计 -->
          <ion-card v-if="summaryData.plant_disease_count && Object.keys(summaryData.plant_disease_count).length">
            <ion-card-header>
              <ion-card-title>植物病害统计</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <ion-list>
                <ion-item v-for="(count, plant) in summaryData.plant_disease_count" :key="plant">
                  <ion-icon slot="start" :icon="bandageOutline"></ion-icon>
                  {{ plant }}: {{ count }}
                </ion-item>
              </ion-list>
            </ion-card-content>
          </ion-card>

          <!-- 病害详情统计 -->
          <ion-card v-if="summaryData.disease_count && Object.keys(summaryData.disease_count).length">
            <ion-card-header>
              <ion-card-title>病害详情统计</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <ion-list>
                <ion-item v-for="(count, disease) in summaryData.disease_count" :key="disease">
                  <ion-icon slot="start" :icon="pulseOutline"></ion-icon>
                  {{ disease }}: {{ count }}
                </ion-item>
              </ion-list>
            </ion-card-content>
          </ion-card>

          <!-- 预测建议 -->
          <ion-card v-if="summaryData.prediction">
            <ion-card-header>
              <ion-card-title>预测建议</ion-card-title>
            </ion-card-header>
            <ion-card-content>
              <ion-text color="success">{{ summaryData.prediction }}</ion-text>
            </ion-card-content>
          </ion-card>
        </div>
      </ion-content>

    </ion-modal>
  </ion-page>
</template>

<script setup lang="ts">
import { IonPage,  IonContent,IonItem,IonCard,IonCardContent,IonCardHeader,IonCardTitle,IonIcon,IonText,IonLabel, IonButton,useIonRouter,IonModal,IonList,IonInput,IonHeader,IonToolbar,IonButtons,IonTitle,IonInputPasswordToggle,IonRadio,IonRadioGroup,IonSelect,IonSelectOption, onIonViewWillEnter } from '@ionic/vue';
import { ref,onMounted,nextTick } from 'vue';
import { presentAlert, errorAlert } from '@/utils/alert';
import { backendUrl } from '@/utils/config';
import { bandageOutline, leafOutline, locationOutline, personCircleOutline, pulseOutline, timeOutline } from 'ionicons/icons';
import storage from "@/utils/storage";
import axios from 'axios';
const ionRouter = useIonRouter();
const username = ref('');
const password = ref('');
const location = ref('');
const sumCount = ref('');

interface InfoResponse {
  userName:string
  password:string
  location:string
  sumCount:string
}
interface CityResponse {
  cityName: string;
  cityCode: string;
}
const fetchInfos = async () => {
  try {
    const token = await (await storage).get('access_token');
    if(!token){
      ionRouter.push("/login");
      return;
    }
    const response = await axios.get<InfoResponse>(backendUrl+'/user/me', { 
      headers: {
        Authorization: `Bearer ${token}` 
      }
     });

    if (response.status === 200) {
      username.value=response.data.userName;
      password.value=response.data.password;
      location.value=response.data.location;
      sumCount.value=response.data.sumCount;
    } else {
      presentAlert("错误","",response.statusText);
    }
  } catch (error:any) {
    errorAlert(error)

  }
};

const logout = async () => {
  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      ionRouter.push("/login");
      return;
    }

    const response = await axios.post(
      `${backendUrl}/user/logout`, 
      {}, 
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status !== 200) {
      presentAlert("错误", "", response.statusText);
      return; 
    }
  } catch (error: any) {
    errorAlert(error);
    return; 
  }
  await (await storage).clear();
  ionRouter.push("/login");
};

const isUpdateModalOpen = ref(false);
const updatedUserName = ref("");
const updatedPassword = ref("");
const repeatPassword = ref("");
const updatedLocation = ref("");
const cityOptions = ref<CityResponse[]>([]);
  const searchKeyword = ref("");

const openUpdateUserModal = () => {
  updatedUserName.value = username.value;
  updatedPassword.value = "";
  repeatPassword.value = "";
  updatedLocation.value = location.value;
  isUpdateModalOpen.value = true;
};

const closeModal = () => {
  isUpdateModalOpen.value = false;
};
const onSearch = async () => {
  if (!searchKeyword.value) {
    cityOptions.value = [];
    return;
  }
  try {
    const response = await axios.get<CityResponse[]>(
      `${backendUrl}/user/city/${encodeURIComponent(searchKeyword.value)}`
    );
    cityOptions.value = response.data;
  } catch (error) {
    console.error("城市搜索失败", error);
    cityOptions.value = [];
  }
};

const onCitySelect = (event: any) => {
  const selectedCity = event.detail.value
  updatedLocation.value = selectedCity;
  searchKeyword.value = selectedCity;
};


const updateUserInfo = async () => {
  if (updatedPassword.value !== repeatPassword.value) {
    presentAlert("错误", "", "密码不匹配，请重试！");
    return;
  }

  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      ionRouter.push("/login");
      return;
    }

    const response = await axios.patch(
      `${backendUrl}/user/update`,
      {
        userName: updatedUserName.value,
        password: updatedPassword.value,
        location: updatedLocation.value,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 200) {
      username.value = updatedUserName.value;
      location.value = updatedLocation.value;
      presentAlert("成功", "", "用户信息已更新！");
      closeModal();
      fetchInfos();
    } else {
      presentAlert("错误", "", response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }


};


interface Package {
  price: number;
  packageId: string;
  packageName: string;
  sumNum: number;
}

const packages = ref<Package[]>([]); 
const selectedPackageId = ref<string>(''); 
const isRechargeModalOpen = ref(false); 

const openRechargeModal = async () => {
  await fetchAvailablePackages(); // 获取套餐信息
  isRechargeModalOpen.value = true; // 打开模态窗口
};

const closeRechargeModal = () => {
  isRechargeModalOpen.value = false; // 关闭模态窗口
};

// 获取可用套餐信息
const fetchAvailablePackages = async () => {
  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      ionRouter.push("/login");
      return;
    }

    const response = await axios.get<Package[]>(`${backendUrl}/user/package`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 200) {
      packages.value = response.data; // 假设返回的套餐数据是数组格式
    } else {
      presentAlert("错误", "获取套餐信息失败", response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};

// 用户确认支付逻辑
const confirmPayment = async () => {
  if (!selectedPackageId.value) {
    presentAlert("错误", "请先选择一个套餐", "");
    return;
  }

  try {
    const token = await (await storage).get('access_token');
    if (!token) {
      ionRouter.push("/login");
      return;
    }

    const response = await axios.post(
      `${backendUrl}/user/recharge/${selectedPackageId.value}`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (response.status === 200) {
      presentAlert("成功", "充值成功", "");
      closeRechargeModal(); // 关闭模态窗口\
      fetchInfos();
    } else {
      presentAlert("错误", "充值失败", response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};
import Chart from "chart.js/auto";

const isSummaryModalOpen = ref(false);
const summaryData = ref<any>(null);
  let monthlyDiseaseChart: Chart<"bar", number[], string> | null = null;

const fetchSummary = async () => {
  try {
    const token = await (await storage).get("access_token");
    if (!token) {
      ionRouter.push("/login");
      return;
    }

    const response = await axios.get(`${backendUrl}/log/summary`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 200) {
      summaryData.value = response.data;
      isSummaryModalOpen.value = true;
      fetchInfos();
    } else {
      presentAlert("错误", "获取总结失败", response.statusText);
    }
  } catch (error: any) {
    errorAlert(error);
  }
};
const renderMonthlyDiseaseChart = async () => {
  if (!summaryData.value || !summaryData.value.monthly_disease_count) {
    console.log("没有找到月病害统计数据！");
    return;
  }

  await nextTick();

  const canvas = document.getElementById("monthlyDiseaseChart") as HTMLCanvasElement;
  if (!canvas) {
    console.error("Canvas 元素未找到！");
    return;
  }

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    console.error("无法获取 Chart.js 的上下文！");
    return;
  }

  const monthlyDiseaseData = summaryData.value.monthly_disease_count;
  const labels = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"];
  const data = {
    labels,
    datasets: [
      {
        label: "每月疾病数量",
        data: monthlyDiseaseData,
        backgroundColor: "rgba(75, 192, 192, 0.2)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  };

  console.log("成功获取 Chart.js 的上下文！");
  monthlyDiseaseChart = new Chart(ctx, {
    type: "bar", // 柱状图
    data,
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
        },
      },
    },
  });
};
const onModalDidPresent = async () => {
  renderMonthlyDiseaseChart();
};


const closeSummaryModal = () => {
  isSummaryModalOpen.value = false;
  if (monthlyDiseaseChart) {
    monthlyDiseaseChart.destroy();
    monthlyDiseaseChart = null;
  }
};
onIonViewWillEnter(() => {
  fetchInfos();
});
</script>
<style scoped>
canvas {
  max-width: 100%;
  margin: 20px auto;
}
</style>
