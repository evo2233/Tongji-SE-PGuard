import { Storage } from '@ionic/storage';

const storage = new Storage();

await storage.create();

//await storage.clear();

export default storage;