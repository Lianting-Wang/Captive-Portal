function getQueryParam(param) {
    const search = window.location.search.substring(1);
    const variables = search.split('&');
    for (let i = 0; i < variables.length; i++) {
        const pair = variables[i].split('=');
        if (pair[0] == param) {
            return pair[1];
        }
    }
    return false;
}

export function getRedirectLink(param='original_host', host='https://google.com') {
    const originalHost = getQueryParam(param);
    return originalHost ? decodeURIComponent(originalHost) : host;
}
