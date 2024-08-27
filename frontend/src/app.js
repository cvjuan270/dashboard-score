const { Component, mount, xml, useState, reactive, onMounted, useRef, onWillStart } = owl


class ChartRenderer extends Component {

    static template = xml`
    <div class="card text-center">
        <div class="card-header">
            <h2><t t-esc="state.title"/></h2>
        </div>
        <canvas t-ref="chart"></canvas>
    </div>
    `
    setup() {
        this.chartRef = useRef("chart");
        this.state = useState({
            title: this.props.title,
            data: this.props.data,
        });

        onWillStart(() => {
            this.socket = new WebSocket("ws://localhost:8000/ws/results");
            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.state.data = data;
                console.log('Chart', data);

                this.render(this.state.title, this.state.data);
            }
        });

        onMounted(() => {
            console.log("Mounted ChartRenderer");
            console.log(this.state.data);
            this.render(this.state.title, this.state.data);
        });
    }

    render(title, data) {
        console.log('Render', data);
        const labels = []
        const metrics = []
        data.map((item) => {
            labels.push(item['name']);
            metrics.push(item['score']);
        });
        if (window.myChart) {
            window.myChart.destroy();
        }



        const colores = {
            'VILADRAU': 'rgba(247, 250, 61, 0.8)',
            'VIC': 'rgba(0, 123, 255, 0.8)',
            'NARBONA': 'rgba(61, 250, 102, 0.8)',
            'SALLENT': 'rgba(250, 61, 140, 0.8)',
        }
        // const bordes = {
        //     'CASA AMARILLA': 'rgba(247, 250, 61, 1)',
        //     'CASA AZUL': 'rgba(0, 123, 255, 1)',
        //     'CASA VERDE': 'rgba(61, 250, 102, 1)',
        //     'CASA ROJA': 'rgba(250, 61, 140, 1)',
        // }
        console.log(labels.map((name) => colores[name]));
        window.myChart = new Chart(this.chartRef.el, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    data: metrics,
                    backgroundColor: labels.map((team) => colores[team]),
                    // borderColor: labels.map((team) => bordes[team]),
                    borderWidth: 1,
                }],

            },
            options: {
                plugins: {
                    legend: {
                        display: false,
                    },
                    datalabels: {
                        anchor: 'end',
                        align: 'top',
                        font: {
                            size: 24,
                            formatter: function (value, context) {
                                return value;  // Muestra el valor directamente
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                font: {
                                    size: 24  // Cambia el tamaño aquí
                                }
                            }
                        }
                    },
                },
                scales: {
                    x: {
                        ticks: {
                            font: {
                                size: 24  // Cambia el tamaño aquí
                            }
                        }
                    },
                    y: {
                        ticks: {
                            font: {
                                size: 24  // Cambia el tamaño aquí
                            }
                        }
                    }
                },
                
            },
            plugins: [ChartDataLabels]  // Habilitar el plugin de data labels
        });
    }
}

class Root extends Component {
    static components = { ChartRenderer };
    static template = xml`
    <div class="container">
        <div class="container-fluid">
        <ChartRenderer title="'Puntos'" data="state.results"/>
        </div>
    </div>
    `
    async setup() {

        this.state = useState({
            results: [],
        });

        this.socket = new WebSocket("ws://localhost:8000/ws/results");
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data);
        }


        onWillStart(async () => {
            this.state.results = await this.fetchResults();
        });

    }

    async setupWebSocket() {
        // Conectar al WebSocket
        socket.on("connect", () => {
            console.log("WebSocket connected");
        });

        // Escuchar los eventos de actualización de resultados
        socket.on("result_update", (data) => {
            this.updateResults(data);
        });

        // Obtener los resultados iniciales
        this.fetchResults();
    }

    // async fetchResults() {
    //     console.log("Fetching results");
    //     const url = 'http://localhost:8000/results';
    //     try {
    //         const response = await fetch(url,
    //             { method: 'GET', headers: { 'Content-Type': 'application/json' } })
    //         const data = await response.json();
    //         return data;
    //     }
    //     catch (error) {
    //         console.error('Error:', error);
    //         return [];
    //     }
    // }

    async fetchResults() {
        console.log("Fetching results");
        const url = 'http://localhost:8000/team_scores_by_team';
        try {
            const response = await fetch(url,
                { method: 'GET', headers: { 'Content-Type': 'application/json' } })
            const data = await response.json();
            console.log(data);
            return data;
        }
        catch (error) {
            console.error('Error:', error);
            return [];
        }
    }
    onWillUnmount() {
        // Desconectar del WebSocket al desmontar el componente
        socket.disconnect();
    }

}

mount(Root, document.getElementById("root"))
