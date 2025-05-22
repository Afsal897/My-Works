console.log("Script loaded");

/**
 * Update the description of a content item.
 * Sends a PUT request with the new description.
 */
async function updateDescription(contentId) {
    const container = document.querySelector(`.content-item[data-id="${contentId}"]`);
    const input = container.querySelector('.edit-input');
    const newDescription = input.value;

    try {
        const response = await fetchWithRefresh(`/edit/${contentId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Include cookies for auth
            body: JSON.stringify({ new_description: newDescription })
        });

        const data = await response.json();
        alert(data.message || data.error);
        location.reload(); // Refresh the page to reflect changes
    } catch (error) {
        alert("Failed to update description. Please try again.");
        console.error("Update error:", error);
    }
}

/**
 * Delete a content item after user confirmation.
 * Sends a DELETE request to the backend.
 */
async function deleteContent(contentId) {
    if (!confirm("Are you sure you want to delete this content?")) return;

    try {
        const response = await fetchWithRefresh(`/delete/${contentId}`, {
            method: 'DELETE',
            credentials: 'include' // Ensure cookies (auth) are included
        });

        const data = await response.json();
        alert(data.message || data.error);
        location.reload(); // Reload page after deletion
    } catch (error) {
        alert("Failed to delete content. Please try again.");
        console.error("Delete error:", error);
    }
}

/**
 * Wraps fetch with automatic JWT refresh if needed.
 * Retries the request once after attempting token refresh.
 */
async function fetchWithRefresh(url, options, retries = 1) {
    try {
        let res = await fetch(url, options);

        // If unauthorized and retries remain, try refreshing token
        if (res.status === 401 && retries > 0) {
            const refreshRes = await fetch('/refresh', {
                method: 'POST',
                credentials: 'include'
            });

            if (refreshRes.ok) {
                // Retry original request after successful refresh
                return fetchWithRefresh(url, options, retries - 1);
            } else {
                // Refresh failed: redirect to login page
                window.location.href = '/';
                return;
            }
        }

        return res;
    } catch (error) {
        console.error("Fetch error:", error);
        throw error;
    }
}