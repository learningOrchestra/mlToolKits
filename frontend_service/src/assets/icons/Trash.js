import React from 'react';

export default ({color='#8D8D8D', size='24'}) => {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M6 7H5V20C5 20.5304 5.21071 21.0391 5.58579 21.4142C5.96086 21.7893 6.46957 22 7 22H17C17.5304 22 18.0391 21.7893 18.4142 21.4142C18.7893 21.0391 19 20.5304 19 20V7H6ZM10 19H8V10H10V19ZM16 19H14V10H16V19ZM16.618 4L15 2H9L7.382 4H3V6H21V4H16.618Z" fill={color}/>
    </svg>
  );
}

