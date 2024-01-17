<template>
  <div id="app">
    <h1 v-show="!gameOver">
      Player {{ currentPlayer }}'s Turn
    </h1>
    <h1 v-show="gameOver">
      <span>
        Player {{ currentPlayer }} Wins!
      </span>
      <!-- <span v-else>It's a Draw!</span> -->
    </h1>
    <div class="settings">
      <div>
        <button @click="playAIvsAI()">AI VS AI</button>
      </div>
    </div>
    <div class="wrapper">
      <div class="board">
        <div class="column" v-for="(column, columnIndex) in board[0]" :key="'col-' + columnIndex"
          :style="{ left: columnIndex * 50 + 'px' }" @click="takeTurn(columnIndex)"></div>
        <div v-for="(row, rowIndex) in board" :key="rowIndex" class="row">
          <svg v-for="(column, columnIndex) in row" :key="columnIndex" width="50" height="50">
            <circle cx="25" cy="25" r="20" :id="'circle-' + rowIndex + '-' + columnIndex" :class="{
              empty: column === empty,
              red: column === red,
              yellow: column === yellow
            }" />
          </svg>
        </div>
      </div>
    </div>
    <button type="button" @click="resetBoard()">Reset</button>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { io } from 'socket.io-client';


function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function highlightPieces(pieces) {
  pieces.forEach(piece => {
    document.getElementById(`circle-${piece.row}-${piece.col}`).classList.add('flash');
  });
}

const board = ref([]);
const turn = ref(0);
const player1 = ref(0);
const player2 = ref(2);
const red = ref(1);
const yellow = ref(2);
const empty = ref();
const gameOver = ref(false);
const currentPlayer = ref(1);


const socket = io('http://localhost:5000');


socket.on('initial_board', (data) => {
  board.value = data.board;
  console.log(data.board);
  console.log(board.value);
});

// reset board
function resetBoard() {
  socket.emit('reset_board');
}

socket.on('update_board', (data) => {
  board.value = data.board;
  gameOver.value = data.game_over;
  currentPlayer.value = data.turn;
  console.log("Updated Board:", data.board);
});

function takeTurn(columnIndex) {
  if (!gameOver.value) {
    const player = currentPlayer.value;
    const piece = player === 1 ? red.value : yellow.value;
    socket.emit('take_turn', { column: columnIndex, piece: red.value });
  }
}

function playAIvsAI() {
  socket.emit('ai_vs_ai');
}

</script>


<style>
#app {
  width: 100%;
  height: 100%;
  background-color: #fff;
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

.wrapper {
  display: flex;
  justify-content: center;
}

.board {
  position: relative;
}

.row {
  display: flex;
  background-color: #0f55ff;
}

.column {
  box-sizing: border-box;
  position: absolute;
  top: 0;
  width: 50px;
  height: 100%;
  transition: background-color 0.1s ease-in-out;
  background-color: transparent;
}

.column:hover {
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0.2);
}

circle.empty {
  fill: #ffffff;
}

circle.red {
  fill: #d50000;
}

circle.yellow {
  fill: #dad400;
}

circle.red.flash {
  animation: pulse-red 1.2s ease-in-out infinite;
}

circle.yellow.flash {
  animation: pulse-yellow 1.2s ease-in-out infinite;
}

button {
  margin-top: 20px;
  padding: 10px;
  border: none;
  border-radius: 5px;
  background-color: #0f55ff;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
}

@keyframes pulse-yellow {
  0% {
    fill: #dad400;
  }

  50% {
    fill: #fffdab;
  }

  100% {
    fill: #dad400;
  }
}

@keyframes pulse-red {
  0% {
    fill: #d50000;
  }

  50% {
    fill: #ff8f8f;
  }

  100% {
    fill: #d50000;
  }
}

.settings {
  display: flex;
  flex-direction: column;
  width: 50%;
  margin: auto;
}

.settings div {
  padding: 10px;
}

.settings label {
  margin-right: 10px;
}
</style>