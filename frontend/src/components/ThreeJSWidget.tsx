import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function ThreeJSWidget() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    // Enhanced Lighting for glossy effect
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const mainLight = new THREE.DirectionalLight(0xffffff, 2);
    mainLight.position.set(5, 10, 7);
    scene.add(mainLight);

    const backLight = new THREE.DirectionalLight(0xa7f3d0, 1.5);
    backLight.position.set(-5, -5, -5);
    scene.add(backLight);

    // Create a smooth glossy sphere
    const geometry = new THREE.SphereGeometry(1.5, 64, 64);
    
    // Using MeshPhysicalMaterial for a premium glass/glossy look
    const material = new THREE.MeshPhysicalMaterial({
      color: 0x10b981, // Emerald green
      emissive: 0x047857, // Darker emerald for depth
      emissiveIntensity: 0.2,
      roughness: 0.1,
      metalness: 0.1,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
      transparent: true,
      opacity: 0.95
    });

    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);

    camera.position.z = 6;

    // Animation
    let animationFrameId: number;
    let time = 0;
    
    function animate() {
      animationFrameId = requestAnimationFrame(animate);
      time += 0.01;
      
      mesh.rotation.x += 0.005;
      mesh.rotation.y += 0.008;
      
      // Gentle floating
      mesh.position.y = Math.sin(time) * 0.15;
      
      renderer.render(scene, camera);
    }

    const handleResize = () => {
      const w = container.clientWidth || window.innerWidth;
      const h = container.clientHeight || window.innerHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);
    animate();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
      renderer.dispose();
      geometry.dispose();
      material.dispose();
    };
  }, []);

  return (
    <div className="absolute inset-0 w-full h-full" style={{ display: 'block' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
