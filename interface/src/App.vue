<template>
  <div id="app">
    <h1 v-show="!gameOver">
      Player <span v-if="turn === player1">1</span><span v-else>2</span>
    </h1>
    <h1 v-show="gameOver">
      Player <span v-if="turn === player1">1</span><span v-else>2</span> Wins!
    </h1>
    <div class="settings">
      <!-- <div>
        <input type="radio" id="easy" v-model="difficulty" value="easy" />
        <label for="easy">Easy</label>
        <input type="radio" id="hard" v-model="difficulty" value="hard" />
        <label for="hard">Hard</label>
      </div> -->
      <div>
        <input type="radio" id="single-p" @click="resetBoard()" v-model="mode" value="SinglePlayer" />
        <label for="single-p">Versus AI</label>
        <input type="radio" id="two-p" @click="resetBoard()" v-model="mode" value="TwoPlayers" />
        <label for="two-p">Two Player Mode</label>
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
    <button v-show="gameOver" type="button" @click="resetBoard()">Reset</button>
  </div>
</template>

<script setup>
import { ref, onMounted, onUpdated } from 'vue';
import axios from 'axios';
import { io } from 'socket.io-client';

const socket = io('http://localhost:5000');

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
const player1 = ref(1);
const player2 = ref(2);
const red = ref(1);
const yellow = ref(2);
const empty = ref(0);
const gameOver = ref(false);
const mode = ref('SinglePlayer');

socket.on('initial_board', (data) => {
  board.value = data.board;
});

socket.on('update_board', (data) => {
  board.value = data.board;
  gameOver.value = data.game_over;
  if (gameOver.value) {
    highlightPieces(data.winning_pieces);
  }
  if (!gameOver.value) {
    turn.value = turn.value === player1.value ? player2.value : player1.value;
  }
  if (!gameOver.value && mode.value === 'SinglePlayer') {
    sleep(500).then(() => {
      takeAITurn();
    });
  }
});



// async function resetBoard() {
//   try {
//     // Make a POST request to reset the board on the Flask server
//     await axios.post('http://localhost:5000/api/reset');
//     // Fetch the initial board state from the server
//     const response = await axios.get('http://localhost:5000/api/board');
//     board.value = response.data.board;
//     gameOver.value = false;
//     turn.value = player1.value;
//   } catch (error) {
//     console.error('Error during board reset:', error);
//   }
// }

// async function takeTurn(columnIndex) {
//   try {
//     console.log('Before axios POST request');
//     const response = await axios.post('http://localhost:5000/api/take_turn', {
//       column: columnIndex,
//       board: board.value,
//     });
//     console.log('After axios POST request', response);

//     board.value = response.data.board;
//     gameOver.value = response.data.game_over;

//     if (gameOver.value) {
//       highlightPieces(response.data.winning_pieces);
//     }

//     if (!gameOver.value) {
//       turn.value = turn.value === player1.value ? player2.value : player1.value;
//     }

//     if (!gameOver.value && mode.value === 'SinglePlayer') {
//       await sleep(500);
//       await takeAITurn();
//     }
//   } catch (error) {
//     console.error('Error during turn:', error);
//   }
// }

// async function takeAITurn() {
//   try {
//     // Make a POST request to the Flask server to take a turn
//     const response = await axios.post('http://localhost:5000/api/take_ai_turn', {
//       difficulty: difficulty.value,
//       player: turn.value,
//     });
//     // Update the board state with the response from the server
//     board.value = response.data.board;
//     // Check if the game is over
//     gameOver.value = response.data.game_over;
//     // If the game is over, highlight the winning pieces
//     if (gameOver.value) {
//       highlightPieces(response.data.winning_pieces);
//     }
//     // If the game is not over, switch the turn to the other player
//     if (!gameOver.value) {
//       turn.value = turn.value === player1.value ? player2.value : player1.value;
//     }
//   } catch (error) {
//     console.error('Error during AI turn:', error);
//   }
// }

// onMounted(() => {
//   // Fetch the initial board state from the server when the component is mounted
//   axios.get('http://localhost:5000/api/get_board').then(response => {
//     console.log(response.data)
//     board.value = response.data.board;
//     console.log(board.value)
//   });
// });

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
  fill: #fff;
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