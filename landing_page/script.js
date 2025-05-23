function revealElements() {
    const elements = document.querySelectorAll('.benefit-item, .process-item');
    elements.forEach(element => {
        const rect = element.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.8) {
            element.classList.add('animated');
        }
    });
}

window.addEventListener('scroll', revealElements);
window.addEventListener('load', revealElements); // To check on initial load