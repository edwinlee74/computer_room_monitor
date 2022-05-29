import { Chart, 
              LineController, 
              CategoryScale, 
              LinearScale, 
              PointElement, 
              LineElement,
              Legend, 
              Tooltip,
              TimeScale,
              TimeSeriesScale  
         } from 'chart.js'

import 'chartjs-adapter-luxon'

Chart.register(LineController,
                      CategoryScale, 
                      LinearScale, 
                      PointElement, 
                      LineElement, 
                      Legend, 
                      Tooltip,
                      TimeScale,
                      TimeSeriesScale)

function initChart(chart_id: string, label_val: string, color: string) {
    return new Chart(<HTMLCanvasElement>document.getElementById(chart_id), 
           {
               type: 'line',
               data: {
                    labels: [],            
                   datasets: [{
                    label: label_val,
                    data: [],
                    fill: false,
                    borderColor: color,
                    tension: 0.1
                }]
             },
             options: {
                  scales: {
                    x: {
                         type: 'time',
                         time: {
                              unit: 'minute'
                         },
                    }
                  }
             }
          })
}

function updateChart(inst: any, data: number[], label: string[]) {
     inst.config.data.datasets[0].data = data;
     inst.config.data.labels = label;
     inst.update();
}

export { initChart, updateChart }