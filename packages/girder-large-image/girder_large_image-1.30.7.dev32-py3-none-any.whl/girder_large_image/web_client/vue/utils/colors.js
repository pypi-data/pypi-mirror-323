export const CHANNEL_COLORS = {
    '^BRIGHTFIELD.*$': '#FFFFFF',
    '^DAPI.*$': '#0000FF',
    '^A594(|[^\d].*)$': '#FF0000',  // eslint-disable-line
    '^CY3(|[^\d].*)$': '#FF8000',  // eslint-disable-line
    '^CY5(|[^\d].*)$': '#FF00FF',  // eslint-disable-line
    '^YFP.*$': '#00FF00',
    '^GFP.*$': '#00FF00',
    '^red$': '#FF0000',
    '^green$': '#00FF00',
    '^blue$': '#0000FF',
    '^gr[ae]y(|scale)$': '#FFFFFF'
};

export function getChannelColor(name, usedColors) {
    // Search for case-insensitive regex match among known channel-colors
    for (const [channelPattern, color] of Object.entries(CHANNEL_COLORS)) {
        if (!usedColors.includes(color) && name.match(new RegExp(channelPattern, 'i'))) {
            usedColors.push(color);
            return color;
        }
    }
}

export const OTHER_COLORS = [
    '#FF0000',
    '#00FF00',
    '#0000FF',
    '#FFFF00',
    '#FF00FF',
    '#00FFFF',
    '#FF8000',
    '#FF0080',
    '#00FF80',
    '#80FF00',
    '#8000FF',
    '#0080FF',
    '#FF8080',
    '#80FF80',
    '#8080FF',
    '#FFFF80',
    '#80FFFF',
    '#FF80FF',
    '#FF4000',
    '#FF0040',
    '#00FF40',
    '#40FF00',
    '#4000FF',
    '#0040FF',
    '#FF4040',
    '#40FF40',
    '#4040FF',
    '#FFFF40',
    '#40FFFF',
    '#FF40FF',
    '#FFC000',
    '#FF00C0',
    '#00FFC0',
    '#C0FF00',
    '#C000FF',
    '#00C0FF',
    '#FFC0C0',
    '#C0FFC0',
    '#C0C0FF',
    '#FFFFC0',
    '#C0FFFF',
    '#FFC0FF',
    '#FF8040',
    '#FF4080',
    '#40FF80',
    '#80FF40',
    '#8040FF',
    '#4080FF',
    '#FF80C0',
    '#FFC080',
    '#C0FF80',
    '#80FFC0',
    '#80C0FF',
    '#C080FF',
    '#FFC040',
    '#FF40C0',
    '#40FFC0',
    '#C0FF40',
    '#C040FF',
    '#40C0FF'
];
