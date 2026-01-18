document.addEventListener('DOMContentLoaded', () => {
    const containers = document.querySelectorAll('.js-star-rating');

    containers.forEach(container => {
        const inputName = container.dataset.name;
        const initialValue = parseInt(container.dataset.value) || 0;

        // Create hidden input
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = inputName;
        hiddenInput.value = initialValue;
        container.appendChild(hiddenInput);

        // Create stars container
        const starsDiv = document.createElement('div');
        starsDiv.className = 'stars-wrapper';
        container.appendChild(starsDiv);

        // Create 5 stars
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('span');
            star.innerHTML = '★'; // or use SVG
            star.dataset.value = i;
            star.className = 'star-item';

            // Events
            star.addEventListener('mouseover', () => highlightStars(starsDiv, i));
            star.addEventListener('mouseout', () => highlightStars(starsDiv, hiddenInput.value));
            star.addEventListener('click', () => {
                hiddenInput.value = i;
                highlightStars(starsDiv, i);
            });

            starsDiv.appendChild(star);
        }

        // Initialize star highlighting based on initial value
        highlightStars(starsDiv, initialValue);
    });

    function highlightStars(wrapper, value) {
        const stars = wrapper.querySelectorAll('.star-item');
        stars.forEach(star => {
            const starVal = parseInt(star.dataset.value);
            if (starVal <= value) {
                star.classList.add('active');
                star.style.color = '#f1c40f';
            } else {
                star.classList.remove('active');
                star.style.color = '#ddd';
            }
        });
    }
});
