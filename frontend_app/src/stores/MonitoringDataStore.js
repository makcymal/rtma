import { defineStore } from "pinia";
import { formatHeaderOutput, formatComputeNodeOutput, computeAvgTotalOutput} from "../utils/prettyMonTable"

// Client can send one of the followings messages:
//     "lsob" - get LiSt Of Batches
//     "head?BATCH" - get table HEADer for BATCH
//     "mstd?BATCH" - STanDard Monitoring subscribe to BATCH
//     "spec?BATCH?LABEL" - get SPECifications of machine with LABEL in BATCH
//     "mext?BATCH?LABEL" - EXTended Monitoring to machine with LABEL in BATCH
//     "stop" - stop subscription


const URL = "ws://127.0.0.1:8082/echo";

export const useMonitoringDataStore = defineStore('monitoringDataStore', {
    state: () => ({
        socket: undefined, // надо объявлять веб-сокет
        connectedToServer: false,
        serverMsgStd: [],
        serverTableHeaderStd: {},
        serverMsgExt: [],
        serverMsgSpc: [],
        serverBatchesList: [],
        avgTotalData: { "avg" : [], "total": []}
      }),
    actions: {
        setSocket() {
            this.socket = new WebSocket(URL);
            this.connectedToServer = true;
        },
        sendMessage(){
          return (msg) => {
          this.socket.send(msg);
          }
        },
        listenMsg(){
          this.socket.addEventListener("message", (event) => {
            let parsed_data = JSON.parse(event.data)
            if (parsed_data.header.split("!")[0] === "spec"){ 
              this.serverMsgSpc = parsed_data;

            } else if (parsed_data.header.split("!")[0] === "mext"){
              this.serverMsgExt.push(parsed_data);

            } else if (parsed_data.header.split("!")[0] === "mstd"){
              let nodeMonitored = false
              for (let i = 0; i < this.serverMsgStd.length; i++){
                if (this.serverMsgStd[i].name === parsed_data.header.split("!")[2]){
                  this.serverMsgStd[i] = formatComputeNodeOutput(parsed_data)
                  nodeMonitored = true
                  break
                }
              }
              if (!nodeMonitored){
                this.serverMsgStd.push(formatComputeNodeOutput(parsed_data))
              }
              this.avgTotalData = computeAvgTotalOutput(this.serverTableHeaderStd, this.serverMsgStd)

            } else if (parsed_data.header.split("!")[0] === "head") {
              this.serverTableHeaderStd = formatHeaderOutput(parsed_data)
              this.serverMsgStd = []
              this.serverMsgExt = []
              this.avgTotalData = { "avg" : [], "total": []}

            } else if (parsed_data.header.split("!")[0] === "lsob"){
              this.serverBatchesList = parsed_data.batches
              this.serverTableHeaderStd = {}
              this.serverMsgStd = []
              this.serverMsgExt = []
              this.avgTotalData = { "avg" : [], "total": []}
            }
            });
        }

    },
    persist: {
        enabled: true,
        strategies: [
          {
            key: 'test-store1',
          },
        ],
      }
})