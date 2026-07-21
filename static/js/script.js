/* ============================================
   PELARIKENYA — Main Script
   Version: 1.0.0
   ============================================ */

(function () {
    'use strict';

    /* -------------------------------------------
       Navbar Scroll Effect
       ------------------------------------------- */

    var navbar = document.getElementById('mainNavbar');

    function handleNavbarScroll() {
        if (!navbar) return;
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    if (navbar) {
        window.addEventListener('scroll', handleNavbarScroll, { passive: true });
        handleNavbarScroll();
    }


    /* -------------------------------------------
       Smooth Scroll for Anchor Links
       ------------------------------------------- */

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') return;

            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });


    /* -------------------------------------------
       Scroll-triggered Fade-in Animations
       ------------------------------------------- */

    var animatedElements = document.querySelectorAll('.fade-in, .slide-up');

    if (animatedElements.length > 0 && 'IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        animatedElements.forEach(function (el) {
            observer.observe(el);
        });
    }


    /* -------------------------------------------
       Project Filter & Search
       ------------------------------------------- */

    var projectsGrid = document.getElementById('projectsGrid');
    var filterButtons = document.querySelectorAll('[data-filter]');
    var searchInput = document.getElementById('projectSearch');

    if (projectsGrid && filterButtons.length > 0) {
        var projectCards = projectsGrid.querySelectorAll('[data-category]');
        var activeFilter = 'all';

        // Filter by category
        filterButtons.forEach(function (btn) {
            btn.addEventListener('click', function () {
                activeFilter = this.getAttribute('data-filter');

                // Update active button style
                filterButtons.forEach(function (b) {
                    b.classList.remove('btn-primary');
                    b.classList.add('btn-outline-primary');
                });
                this.classList.remove('btn-outline-primary');
                this.classList.add('btn-primary');

                applyFilters();
            });
        });

        // Search by name, description, or tech
        if (searchInput) {
            searchInput.addEventListener('input', function () {
                applyFilters();
            });
        }

        function applyFilters() {
            var query = searchInput ? searchInput.value.toLowerCase().trim() : '';
            var visibleCount = 0;

            projectCards.forEach(function (card) {
                var category = card.getAttribute('data-category');
                var title = card.querySelector('.card-title');
                var text = card.querySelector('.card-text');
                var badges = card.querySelectorAll('.badge-tech');

                var titleText = title ? title.textContent.toLowerCase() : '';
                var descText = text ? text.textContent.toLowerCase() : '';
                var badgeText = '';
                badges.forEach(function (b) {
                    badgeText += ' ' + b.textContent.toLowerCase();
                });

                var allText = titleText + ' ' + descText + ' ' + badgeText;

                var matchCategory = activeFilter === 'all' || category === activeFilter;
                var matchSearch = query === '' || allText.indexOf(query) !== -1;

                if (matchCategory && matchSearch) {
                    card.style.display = '';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Show/hide empty state
            var emptyState = document.getElementById('projectsEmpty');
            if (visibleCount === 0) {
                if (!emptyState) {
                    var div = document.createElement('div');
                    div.id = 'projectsEmpty';
                    div.className = 'col-12 text-center py-5';
                    div.innerHTML = '<p class="text-muted">No projects found matching your criteria.</p>';
                    projectsGrid.appendChild(div);
                }
            } else if (emptyState) {
                emptyState.remove();
            }
        }
    }

})();
