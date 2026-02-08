document.addEventListener('DOMContentLoaded', () => {
    // Reveal animations on scroll
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // Apply reveal classes
    const revealElements = document.querySelectorAll('.feature-card, .section-header, .monad-feat, .cta-box');
    revealElements.forEach(el => {
        el.classList.add('reveal');
        observer.observe(el);
    });

    // Simple parallax effect for hero glow
    window.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX / window.innerWidth;
        const mouseY = e.clientY / window.innerHeight;

        const blobs = document.querySelectorAll('.glow-blob');
        blobs.forEach((blob, index) => {
            const speed = (index + 1) * 20;
            const x = (mouseX - 0.5) * speed;
            const y = (mouseY - 0.5) * speed;
            blob.style.transform = `translate(${x}px, ${y}px)`;
        });
    });

    // Mockup button interaction
    const betButtons = document.querySelectorAll('.bet-btn');
    betButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.classList.contains('yes') ? 'YES' : 'NO';
            btn.textContent = 'Betting...';
            setTimeout(() => {
                btn.textContent = `Voted ${type}!`;
                btn.style.opacity = '0.7';
                btn.style.pointerEvents = 'none';
            }, 1000);
        });
    });
});
