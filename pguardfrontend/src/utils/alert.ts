import { alertController } from '@ionic/core';

export const presentAlert = async (header: string, subHeader: string, message: string) => {
  const alert = await alertController.create({
    header: header,          // 标题
    subHeader: subHeader,    // 子标题
    message: message,        // 消息
    buttons: ['OK']          // 按钮
  });

  await alert.present();
};
export const errorAlert = async (error:any) => {
  const errorMessage =
      error.response?.data?.message ||
      error.message ||                 
      "未知错误";                     

  presentAlert("错误", "", errorMessage);
};