document.querySelectorAll("[data-quiz]").forEach((quiz) => {
  const button = quiz.querySelector("button");
  const feedback = quiz.querySelector("[data-feedback]");

  button.addEventListener("click", () => {
    const selected = quiz.querySelector("input:checked");

    if (!selected) {
      feedback.textContent = "请先选一项。";
      feedback.className = "incorrect";
      return;
    }

    const isCorrect = selected.value === quiz.dataset.answer;
    feedback.textContent = isCorrect
      ? `正确。${quiz.dataset.correct}`
      : `再想想。${quiz.dataset.incorrect}`;
    feedback.className = isCorrect ? "correct" : "incorrect";
  });
});
