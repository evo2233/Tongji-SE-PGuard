import { Storage } from '@ionic/storage';

const storage = new Storage();

async function initStorage() {
  await storage.create();
  return storage;
}

export default initStorage();