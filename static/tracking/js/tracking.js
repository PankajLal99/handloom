// Track scroll events
let lastScrollPosition = 0;
let scrollTimeout;

document.addEventListener('DOMContentLoaded', function() {
    // Get the current page view ID from the meta tag
    const pageViewId = document.querySelector('meta[name="page-view-id"]')?.content;
    
    if (pageViewId) {
        // Track scroll events
        window.addEventListener('scroll', function() {
            clearTimeout(scrollTimeout);
            
            scrollTimeout = setTimeout(function() {
                const currentScroll = window.pageYOffset;
                const scrollDirection = currentScroll > lastScrollPosition ? 'down' : 'up';
                
                // Get the element at the current scroll position
                const element = document.elementFromPoint(
                    window.innerWidth / 2,
                    currentScroll + window.innerHeight / 2
                );
                
                // Send scroll event to server
                fetch('/tracking/scroll/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        page_view_id: pageViewId,
                        scroll_position: currentScroll,
                        scroll_direction: scrollDirection,
                        element_id: element?.id || null,
                        element_class: element?.className || null,
                        element_type: element?.tagName?.toLowerCase() || null
                    })
                });
                
                lastScrollPosition = currentScroll;
            }, 100); // Debounce scroll events
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 