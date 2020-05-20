<template>
    <div class="wrapper">
        <div class="chat d-flex ">
            <div id="chat-container" class="card card-chat">
                <div class="card-header text-white text-center font-weight-bold subtle-blue-gradient chat-header">
                    Отправь URL друзьям чтобы начать общение
                </div>
                <div class="card-body">
                <div v-on:scroll.passive="arrowTarget" class="container chat-body" id="chat-body" >
                  <div id="arrowscrolldown" @click="onClickArrow">
                    <div  class="wrapper__arrow">
                      <div class="wrapper__img_arrow">
                        <img  src="../assets/down-arrow.png" class="arrow" alt="">
                      </div>
                    </div>
                  </div>
                    <div v-for="message in messages" :key="message.id"  class="row chat-section d-flex flex-column">
                      <template v-if="username === message.user.username" v-on:scroll.passive="messageChatSection">
                        <div class="col-sm-7 offset-5">
                          <p class="card-text speech-bubble speech-bubble-user float-right text-white subtle-blue-gradient">
                          {{ message.message }}
                        <span v-for="reader in message.readers" :key="reader.id">
                          {{reader.reader.username}} читатель
                         </span>
                         </p>
                        </div>
                      </template>
                      <template v-else>
                        <div class="col-sm-7">
                          <div :id="['Message_'+message.id]" :class="isAnotherMessage(message.readers)? '': 'anothermessage' " class=" speech-bubble speech-bubble-peer text-left" >
                            <span class="nicname">{{message.user.username}}</span>
                            <p>{{message.message}} </p>
                          <span v-for="reader in message.readers" :key="reader.id">
                          {{reader.reader.username }} читатель
                         </span>
                          </div>
                        </div>
                      </template>
                    </div>
                  </div>
                </div>
                <div class="card-footer text-muted ">
                    <form>
                    <div class="row">
                        <form @submit.prevent="postMessage" class="col-sm-12 d-flex justify-content-center">
                            <input v-model="message" type="text" class="" placeholder="Введите сообщение" />
                            <button class="pushbtn">
                              Отправить
                            </button>
                        </form>
                    </div>
                    </form>
                </div>
              </div>
                <div class="members">
                  <div class="card card-members d-flex flex-column">
                    <div class="card-header members-header subtle-blue-gradient text-white text-center">
                      <p>Участники</p>
                    </div>
                    <div class="card-body members-body">
                      <div class="constainer ">
                        <div v-for="member in members" :key="member.id" class="row members-section d-flex flex-column">
                            <ul>
                              <li>{{member.username}}</li>
                            </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
            </div>
            </div>
</template>

<script>
import axios from 'axios'
export default {
  data () {
    return {
      messages: [],
      message: '',
      members: [],
      isArrow: false,
      username: ''
    }
  },
  created () {
    this.username = sessionStorage.getItem('username')
    axios.defaults.headers.common['Authorization'] = 'Token ' + sessionStorage.getItem('authToken')
    if (this.$route.params.uri) {
      this.joinChatSession()
    } else {
      this.startChatSession()
    }
    
  },
  mounted() {
    
  },
  methods: {
    startChatSession () {
      const api = 'http://localhost:8000/api/chats/'
      axios.post(api)
        .then((response) => {
          console.log("A new session has been created you'll be redirected automatically")

          this.$router.push(`/chats/${response.data.uri}/`)
          this.getMembers()
          this.connectToWebSocket()
        })
        .catch((e) => {
          console.log(e.response)
        })
    },
    postMessage () {
      const data = {message: this.message}

      axios.post(`http://localhost:8000/api/chats/${this.$route.params.uri}/messages/`, data)
        .then(() => {
          this.message = ''
        })
        .catch((response) => {
          alert(response.responseText)
        })
    },
    async joinChatSession () {
      const uri = this.$route.params.uri
      const api = 'http://localhost:8000/api/chats/' + uri + '/'
      const respone = await axios({
        method: 'patch',
        url: api,
        data: {username: this.username}
      })
      const user = await respone.data.members.find((member) => member.username === this.username)
      if (user) {
        await this.fetchChatSessionHistory()
        await this.connectToWebSocket()
      }
    },
    async getMembers () {
      const uri = this.$route.params.uri
      const api = 'http://localhost:8000/api/chats/' + uri + '/'
      const respone = await axios(api)
      this.members = respone.data.members
    },
    async fetchChatSessionHistory () {
      await this.getMembers()
      const respone = await axios({
        method: 'get',
        url: `http://127.0.0.1:8000/api/chats/${this.$route.params.uri}/messages/`,
      })
      this.messages = respone.data.messages
    },
    connectToWebSocket () {
      const websocket = new WebSocket(`ws://localhost:8081/${this.$route.params.uri}/`)
      websocket.onopen = this.onOpen
      websocket.onclose = this.onClose
      websocket.onmessage = this.onMessage
      websocket.onerror = this.onError
    },

    onOpen (event) {
      console.log('Connection opened.', event.data)
    },

    onClose (event) {
      console.log('Connection closed.', event.data)
      // Try and Reconnect after five seconds
      setTimeout(this.connectToWebSocket, 5000)
    },

    onMessage (event) {
      const message = JSON.parse(event.data)
      console.log(message)
      if (Object.prototype.hasOwnProperty.call(message,'member')) {
        this.members.push(message.member)
      }
      if (Object.prototype.hasOwnProperty.call(message,'message')) {
        this.messages.push(message)
      }
    },

    onError (event) {
      alert('An error occured:', event.data)
    },
    onClickArrow () {
      let chatBody = this.$el.querySelector('#chat-body')
      chatBody.scrollTop = chatBody.scrollHeight
    },
    arrowTarget () {
      const chatBody = this.$el.querySelector('#chat-body')
      
      
      this.messageReading()
      console.log(Math.round(chatBody.scrollTop) + 'текущая высота')
      console.log(chatBody.scrollHeight - chatBody.clientHeight + 'высота скрола')
      if ((chatBody.scrollHeight - chatBody.clientHeight) !== Math.round(chatBody.scrollTop)) {
        this.$el.querySelector('#arrowscrolldown').style.display = 'flex'
      } else {
        this.$el.querySelector('#arrowscrolldown').style.display = 'none'
      }
    },
    isReading (el){
      let coords = el.getBoundingClientRect();
      console.log(coords)
      let chatBodyHeight = document.querySelector('#chat-body').offsetHeight;
      console.log(chatBodyHeight)
      // видны верхний ИЛИ нижний край элемента
      let topVisible = coords.top > 0 && coords.top <= chatBodyHeight;
      let bottomVisible = coords.bottom <= chatBodyHeight && coords.bottom > 0;

      return topVisible || bottomVisible;
    },
    async messageReading (){
      const uri = this.$route.params.uri
      const api = 'http://localhost:8000/api/chats/' + uri + '/messages/'
      console.log('--------------------новое чтение-------------------')
      for (let message of this.$el.querySelectorAll('.anothermessage')) {
        if (this.isReading(message)) {
          const id = Number(message.getAttribute('id').replace(/[^\d]/g, ''))

          console.log(id)
          
          for(let i=0; i< this.messages.length; i++){
            if(this.messages[i].id === id){
              message.classList.remove('anothermessage') 
              const response = await axios({
                method: 'patch',
                url: api,
                data: {
                  username: this.username,
                  message: this.messages[i]
                  }
              })
              console.log(response.data)
            }
            else{
              continue
            }
          }
          console.log('прочитано')
        }
      } 
    },
    isAnotherMessage(readers){
        for(let i=0;i<readers.length;i++){

          if(readers[i].reader.username === this.username){
            return true
          }
          
        }
        return false
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css?family=Poppins');
.wrapper {
    display: flex;
    align-items: center;
    flex-direction: column;
    justify-content: center;
    width: 100%;
    height: 600px;
    padding: 20px;
    font-family: "Poppins", sans-serif;
}
.nicname{
  color:#838c91;
  font-size:11px;
  border-bottom: 1px solid #56baef ;
}
p{
  margin:0;
}
.chat {
    -webkit-border-radius: 10px 10px 10px 10px;
    border-radius: 10px 10px 10px 10px;
    background: #fff;
    padding: 30px;
    height: 100%;
    width: 90%;
    max-width: 800px;
    position: relative;
    padding: 0px;
    -webkit-box-shadow: 0 30px 60px 0 rgba(0, 0, 0, 0.3);
    box-shadow: 0 30px 60px 0 rgba(0, 0, 0, 0.3);
    text-align: center;
}
#chat-container{

    width: 68%;
    background-color: #f6f6f6;
    height:100%;
}
.members{
  width: 32%;
  height: 100%;
}
.card-chat{
  border-radius: .25rem 0 0 .25rem;
}
.card-members{
  border-radius: 0 .25rem .25rem 0;
  height: 100%;
}
.card-header a {
  text-decoration: underline;
  height:20%;
}

.card-body {
  background-color: #ddd;
  height: 100%;
  padding-top:0px;
  padding-right: 0px;
  padding-left: 0px;
  padding-bottom: 0px;
}

.chat-header{
  border-radius: calc(.25rem - 1px) 0 0 0;
}
#arrowscrolldown{
  z-index: 1;
  position: sticky;
  right: 10px;
  top: 90%;
  width: 100%;
  display: none;
  justify-content: flex-end;
}

.wrapper__img_arrow{
  background-color: #fff;
   justify-content: center;
   display: flex;
  align-content: center;
  border-radius: 50%;
}
.wrapper__arrow{
  background-color: #fff;
  -webkit-box-shadow: 0 30px 60px 0 rgba(0,0,0,0.4);
  box-shadow: 0 30px 60px 0 rgba(0,0,0,0.4);
  border-radius: 50%;
  width: 40px;
  height: 40px;
}
.wrapper__img_arrow:hover{
  background-color: rgba(0, 0, 0, 0.2);
  border: #648ba0 solid 1px;
  cursor: pointer;
}
.arrow{
  width: 100%;
}

.members-header{
  border-radius: 0 calc(.25rem - 1px) 0 0;
}
.members-body{
  height: 100%;
  width: 100%;
  background-color: #fff;
}
.members-section:first-child {
  margin-top: 10px;
}

.members-section {
  margin-top: 15px;
}


#chat-body {
  height: 100%;
  overflow-y: auto;
  max-height: 448px;

}
.card-footer {
    padding:5px 5px;
}
.speech-bubble {

  position: relative;
  border-radius: 0.4em;
  padding: 10px;
  background-color: #fff;
  font-size: 14px;
  -webkit-transition: all 0.5s ease-in-out;
  -moz-transition: all 0.5s ease-in-out;
  -ms-transition: all 0.5s ease-in-out;
  -o-transition: all 0.5s ease-in-out;
  transition: all 0.5s ease-in-out;
}

.subtle-blue-gradient {
  background-color: rgb(84, 186, 237);
}
.anothermessage{
  background-color: rgba(0, 0, 0, 0.2);
}
.chat-section {
  margin-top: 8px;
  margin-bottom: 8px;
}

.send-section {
  margin-bottom: -20px;
  padding-bottom: 10px;
}
.pushbtn  {
  background-color: #56baed;
  border: none;
  color: white;
  padding: 9px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  text-transform: uppercase;
  font-size: 13px;

  -webkit-border-radius: 0px 5px 5px 0px;
  border-radius: 0px 5px 5px 0px;
  width:20%;
  -webkit-transition: all 0.3s ease-in-out;
  -moz-transition: all 0.3s ease-in-out;
  -ms-transition: all 0.3s ease-in-out;
  -o-transition: all 0.3s ease-in-out;
  transition: all 0.3s ease-in-out;
}
.pushbtn:hover {
  background-color: #39ace7;

}

.pushbtn:active  {
  -moz-transform: scale(0.98);
  -webkit-transform: scale(0.98);
  -o-transform: scale(0.98);
  -ms-transform: scale(0.98);
  transform: scale(0.98);

}
.pushbtn:focus {
  outline: none;
  border-right: none;
}
input[type=text]  {
  background-color: #f6f6f6;
  border: none;
  color: #0d0d0d;
  padding: 15px 10px;

  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin:0;
  width: 87%;
  border: 2px solid #f6f6f6;
  -webkit-transition: all 0.5s ease-in-out;
  -moz-transition: all 0.5s ease-in-out;
  -ms-transition: all 0.5s ease-in-out;
  -o-transition: all 0.5s ease-in-out;
  transition: all 0.5s ease-in-out;
  -webkit-border-radius: 5px 0px 0px 5px;
  border-radius: 5px 0px 0px 5px;
}
input[type=text]:focus, input[type=password]:focus {
  background-color: #fff;
  border-bottom: 2px solid #5fbae9;
  outline:none;
}

input[type=text]:placeholder {
  color: #cccccc;
}
* {
  box-sizing: border-box;
}
</style>
