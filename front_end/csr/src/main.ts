import './style.css'
import { renderTime } from './clock'
import { io } from "socket.io-client"
import { initChart, updateChart } from './myChart'
import { thLabelShow, fanOnOff, showMessage } from './myFunction'

window.onload = () => {
  const tChart = initChart('tChart', '一日溫度', 'rgb(82, 52, 235');
  const hChart = initChart('hChart', '一日濕度', 'rgb(143, 235, 52)');
  setInterval(renderTime, 40);
  const socket = io("http://localhost:8000");
  socket.emit('thHistory');
  setInterval(() => socket.emit('thHistory'), 60000)
  socket.on("th_history", (data) => { 
        updateChart(tChart, data.t_value, data.t_time);
        updateChart(hChart, data.h_value, data.h_time);
  });
  socket.on("fan", (data) => {
    fanOnOff(data);
  });
  socket.on("message", (data) => {
    showMessage(data);
  });
  socket.on("th_value", (data) => {
    thLabelShow(data);
  })
} 