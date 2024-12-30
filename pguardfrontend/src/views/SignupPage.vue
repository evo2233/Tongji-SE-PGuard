<template>
  <ion-page>
    <ion-header>
      <ion-toolbar>
        <ion-buttons slot="start">
          <ion-back-button></ion-back-button>
        </ion-buttons>
        <ion-title>注册</ion-title>
      </ion-toolbar>
    </ion-header>

    <ion-content fullscreen>
      <ion-grid class="ion-text-center" style="height: 100%;">
        <ion-row class="ion-justify-content-center ion-align-items-center" style="height: 100%;">
          <ion-col size="12" size-sm="8" size-md="6" size-lg="4">
            <ion-item>
              <ion-input v-model="username" type="text" label="用户名"></ion-input>
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
            <ion-item>
              <ion-input v-model="password" type="password" label="密码">
                <ion-input-password-toggle slot="end"></ion-input-password-toggle>
              </ion-input>
            </ion-item>

            <ion-item>
              <ion-input v-model="confirmpassword" type="password" label="确认密码">
                <ion-input-password-toggle slot="end"></ion-input-password-toggle>
              </ion-input>
            </ion-item>
            <ion-button expand="block" @click="signup">注册</ion-button>
          </ion-col>
        </ion-row>
      </ion-grid>
    </ion-content>
  </ion-page>
</template>

<script setup lang="ts">
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonInput,
  IonItem,
  IonInputPasswordToggle,
  IonButton,
  IonButtons,
  IonBackButton,
  IonGrid,
  IonCol,
  IonRow,
  IonSelect,
  IonSelectOption
} from "@ionic/vue";
import { useIonRouter } from "@ionic/vue";
import { ref } from "vue";
import { backendUrl } from "@/utils/config";
import axios from "axios";
import { presentAlert, errorAlert } from "@/utils/alert";

interface CityResponse {
  cityName: string;
  cityCode: string;
}

const username = ref("");
const searchKeyword = ref("");
const location = ref("");
const password = ref("");
const confirmpassword = ref("");
const cityOptions = ref<CityResponse[]>([]);
const ionRouter = useIonRouter();

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
  location.value = selectedCity;
  searchKeyword.value = selectedCity;
};

const signup = async () => {
  if (!username.value || !password.value || !confirmpassword.value || !location.value) {
    presentAlert("请输入用户名、所在地和密码", "", "");
    return;
  }
  if (password.value != confirmpassword.value) {
    presentAlert("两次输入的密码不同，请重试", "", "");
    return;
  }

  try {
    const response = await axios.post(backendUrl + "/user/signup", {
      userName: username.value,
      password: password.value,
      location: location.value
    });

    if (response.status === 200) {
      presentAlert("注册成功", "", "");
      ionRouter.push("/login");
    } else {
      presentAlert("注册失败", "", "");
    }
  } catch (error: any) {
    errorAlert(error);
  }
};
</script>
