<template>
  <div id="app">
    <h1 v-show="!gameOver">
      Player <span v-if="turn == player1">1</span><span v-else>2</span>
    </h1>
    <h1 v-show="gameOver">
      Player <span v-if="turn == player1">1</span><span v-else>2</span> Wins!
    </h1>
    <div class="settings">
      <div>
        <input type="radio" id="easy" v-model="difficulty" value="easy" />
        <label for="easy">Easy</label>
        <input type="radio" id="hard" v-model="difficulty" value="hard" />
        <label for="easy">Hard</label>
      </div>
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
              empty: column == empty,
              red: column == red,
              yellow: column == yellow
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
import * as connect4 from './connect4';

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function highlightPieces(pieces) {
  pieces.forEach(piece => {
    document.getElementById(`circle-${piece.row}-${piece.col}`).classList.add('flash');
  });
}

const board = ref(connect4.createBoard());
const turn = ref(0);
const player1 = ref(0);
const player2 = ref(1);
const red = ref(connect4.Red);
const yellow = ref(connect4.Yellow);
const empty = ref(connect4.Empty);
const gameOver = ref(false);
const difficulty = ref('easy');
const mode = ref('SinglePlayer');

function takeTurn(column) {
  if (
    !gameOver.value &&
    (turn.value === player1.value ||
      (turn.value === player2.value && mode.value === 'TwoPlayers')) &&
    connect4.isValidColumn(board.value, column)
  ) {
    const row = connect4.getOpenRow(board.value, column);
    const color = turn.value === player1.value ? red.value : yellow.value;
    connect4.dropPiece(board.value, row, column, color);
    if (connect4.isWinningMove(board.value, color)) {
      gameOver.value = true;
    } else {
      turn.value += 1;
      turn.value %= 2;
      if (mode.value === 'SinglePlayer') {
        sleep(1000).then(() => {
          AITurn();
        });
      }
    }
    console.log(board.value);
  }
}

function AITurn() {
  let column = 0;
  if (difficulty.value === 'easy') {
    column = selectBestColumn();
  } else {
    const result = connect4.minimax(board.value, 2, -Infinity, Infinity, true);
    column = result.column;
  }
  const row = connect4.getOpenRow(board.value, column);
  connect4.dropPiece(board.value, row, column, yellow.value);
  if (connect4.isWinningMove(board.value, yellow.value)) {
    gameOver.value = true;
  } else {
    turn.value += 1;
    turn.value %= 2;
  }
}

function selectBestColumn() {
  const validColumns = connect4.getValidColumns(board.value);
  let highestScore = -1000;
  let column = Math.floor(Math.random() * validColumns.length);
  for (let i = 0; i < validColumns.length; i++) {
    const newColumn = validColumns[i];
    const row = connect4.getOpenRow(board.value, newColumn);
    const boardCopy = connect4.copyBoard(board.value);
    connect4.dropPiece(boardCopy, row, newColumn, yellow.value);
    const newScore = connect4.boardScore(boardCopy);
    if (newScore > highestScore) {
      highestScore = newScore;
      column = newColumn;
    }
  }
  return column;
}

function resetBoard() {
  board.value = connect4.createBoard();
  gameOver.value = false;
  turn.value = player1.value;
}

onMounted(() => {
  board.value = connect4.createBoard();
});

onUpdated(() => {
  if (gameOver.value) {
    const color = turn.value === player1.value ? red.value : yellow.value;
    const winningPieces = connect4.getWinningPieces(board.value, color);
    highlightPieces(winningPieces);
  }
});
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
