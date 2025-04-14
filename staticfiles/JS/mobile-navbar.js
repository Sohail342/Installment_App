/**
 * Mobile Navbar - Responsive and Interactive Navigation
 * This script handles the mobile navigation functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const dropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');
    
    // Toggle mobile menu
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', function() {
            // Toggle aria-expanded attribute
            const expanded = menuButton.getAttribute('aria-expanded') === 'true';
            menuButton.setAttribute('aria-expanded', !expanded);
            
            // Toggle menu visibility
            mobileMenu.classList.toggle('mobile-menu-open');
            
            // Toggle icon between bars and X
            const icon = menuButton.querySelector('i');
            if (icon) {
                if (icon.classList.contains('fa-bars')) {
                    icon.classList.remove('fa-bars');
                    icon.classList.add('fa-times');
                } else {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
            
            // Prevent body scrolling when menu is open
            document.body.classList.toggle('overflow-hidden');
        });
    }
    
    // Handle dropdown toggles in mobile menu with improved animation
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Get the dropdown content
            const dropdownContent = this.nextElementSibling;
            
            // Toggle aria-expanded
            const expanded = this.getAttribute('aria-expanded') === 'true';
            this.setAttribute('aria-expanded', !expanded);
            
            // Toggle dropdown visibility with smooth animation
            if (dropdownContent) {
                if (expanded) {
                    // Close dropdown
                    dropdownContent.style.opacity = '0';
                    dropdownContent.style.maxHeight = '0';
                    setTimeout(() => {
                        dropdownContent.classList.remove('mobile-dropdown-open');
                    }, 300);
                } else {
                    // Open dropdown
                    dropdownContent.classList.add('mobile-dropdown-open');
                    dropdownContent.style.maxHeight = dropdownContent.scrollHeight + 'px';
                    dropdownContent.style.opacity = '1';
                }
                
                // Toggle icon rotation
                const icon = this.querySelector('svg');
                if (icon) {
                    icon.classList.toggle('rotate-180');
                }
            }
        });
    });
    
    // Close mobile menu on window resize (if screen becomes larger)
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 1024 && mobileMenu && mobileMenu.classList.contains('mobile-menu-open')) {
            // Reset menu state
            mobileMenu.classList.remove('mobile-menu-open');
            
            // Reset button state
            if (menuButton) {
                menuButton.setAttribute('aria-expanded', 'false');
                const icon = menuButton.querySelector('i');
                if (icon) {
                    icon.classList.remove('fa-times');
                    icon.classList.add('fa-bars');
                }
            }
            
            // Reset body scroll
            document.body.classList.remove('overflow-hidden');
            
            // Reset all dropdowns
            document.querySelectorAll('.mobile-dropdown-open').forEach(dropdown => {
                dropdown.classList.remove('mobile-dropdown-open');
                dropdown.style.maxHeight = '0';
            });
            
            // Reset all dropdown toggles
            document.querySelectorAll('.mobile-dropdown-toggle').forEach(toggle => {
                toggle.setAttribute('aria-expanded', 'false');
                const icon = toggle.querySelector('svg');
                if (icon) {
                    icon.classList.remove('rotate-180');
                }
            });
        }
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(e) {
        if (mobileMenu && mobileMenu.classList.contains('mobile-menu-open')) {
            // Check if click is outside the mobile menu and not on the menu button
            if (!mobileMenu.contains(e.target) && !menuButton.contains(e.target)) {
                // Close the menu
                mobileMenu.classList.remove('mobile-menu-open');
                
                // Reset button state
                if (menuButton) {
                    menuButton.setAttribute('aria-expanded', 'false');
                    const icon = menuButton.querySelector('i');
                    if (icon) {
                        icon.classList.remove('fa-times');
                        icon.classList.add('fa-bars');
                    }
                }
                
                // Reset body scroll
                document.body.classList.remove('overflow-hidden');
            }
        }
    });
});