import { createRouter, createWebHistory } from "vue-router";
import Fortune from "../views/Fortune.vue";

const routes = [
  {
    path: "/fortune",
    name: "Fortune",
    component: Fortune,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
