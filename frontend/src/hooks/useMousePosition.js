import { useState, useEffect } from 'react';

export const useMousePosition = (elementRef) => {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (elementRef.current) {
        const rect = elementRef.current.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        elementRef.current.style.setProperty('--mouse-x', `${x}px`);
        elementRef.current.style.setProperty('--mouse-y', `${y}px`);
        
        setPosition({ x, y });
      }
    };

    const element = elementRef.current;
    if (element) {
      element.addEventListener('mousemove', handleMouseMove);
    }

    return () => {
      if (element) {
        element.removeEventListener('mousemove', handleMouseMove);
      }
    };
  }, [elementRef]);

  return position;
};
