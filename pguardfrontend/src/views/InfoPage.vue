<template>
  <ion-page>
    <ion-content :fullscreen="true">
      <ion-item>
        <!-- <ion-thumbnail slot="start">
          <img alt="头像" :src="" />
        </ion-thumbnail> -->
        <ion-label>{{ username }}</ion-label>
      </ion-item>
      <ion-item>
        <ion-label>所在地: {{ location }}</ion-label>
      </ion-item>
      <ion-item>
        <ion-label>剩余使用次数: {{ sumCount }}</ion-label>
      </ion-item>
      <ion-item>
        <ion-button expand="block" @click="">年终总结</ion-button>
        <ion-button expand="block" @click="openRechargeModal">套餐充值</ion-button>
        <ion-button expand="block" @click="openUpdateUserModal">更改用户信息</ion-button>
        <ion-button expand="block" @click="logout">退出登录</ion-button>
      </ion-item>
    </ion-content>


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
        <ion-button expand="block" @click="updateUserInfo">提交</ion-button>
      </ion-content>
    </ion-modal>
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
          <ion-button expand="block" @click="confirmPayment">支付</ion-button>
        </ion-content>
      </ion-modal>
  </ion-page>
</template>

<script setup lang="ts">
import { IonPage,  IonContent,IonItem,IonThumbnail,IonLabel, IonButton,useIonRouter,IonModal,IonList,IonInput,IonHeader,IonToolbar,IonButtons,IonTitle,IonInputPasswordToggle,IonRadio,IonRadioGroup,IonSelect,IonSelectOption } from '@ionic/vue';
import { ref,onMounted } from 'vue';
import { presentAlert, errorAlert } from '@/utils/alert';
import { backendUrl } from '@/utils/config';
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
    const token = await storage.get('access_token');
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
    const token = await storage.get('access_token');
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
  await storage.remove("access_token");
  await storage.remove("refresh_token");
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
    const token = await storage.get('access_token');
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

onMounted(() => {
  fetchInfos();
});

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
    const token = await storage.get('access_token');
    if (!token) {
      ionRouter.push("/login");
      return;
    }

    const response = await axios.get<Package[]>(`${backendUrl}/user/recharge`, {
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
    const token = await storage.get('access_token');
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

</script>
