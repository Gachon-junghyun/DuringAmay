// tailwind.config.js
module.exports = {
     content: ["./src/**/*.{js,jsx,ts,tsx}"], // 경로 설정 확인
     theme: {
       extend: {
         animation: {
           wiggle: 'wiggle 0.4s ease-in-out',
         },
         keyframes: {
           wiggle: {
             '0%, 100%': { transform: 'rotate(-1deg)' },
             '50%': { transform: 'rotate(1deg)' },
           },
         },
       },
     },
     plugins: [],
   };
   