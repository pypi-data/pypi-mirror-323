#Imports
import time
import pygame
import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Union
from pygame.locals import *
from pygame.event import Event
from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, KEYDOWN
from OpenGL.GL import *
from OpenGL.GLU import *
from scipy.spatial.transform import Rotation as R
from abc import ABC, abstractmethod
import argparse
@dataclass

class Material:
  
    ambient: Tuple[float, float, float, float] = (0.2, 0.2, 0.2, 1.0)
    diffuse: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0)
    specular: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    shininess: float = 64.0
    emission: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)
    
    def apply(self) -> None:
       
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, self.ambient)
        glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, self.diffuse)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, self.specular)
        glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, self.emission)
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, self.shininess)      
class Light:
  
    def __init__(self, 
                 position: Tuple[float, float, float, float],
                 ambient: Tuple[float, float, float, float],
                 diffuse: Tuple[float, float, float, float],
                 specular: Tuple[float, float, float, float],
                 attenuation: Tuple[float, float, float] = (1.0, 0.0014, 0.000007)):
 
        self.position = np.array(position, dtype=np.float32)
        self.ambient = np.array(ambient, dtype=np.float32)
        self.diffuse = np.array(diffuse, dtype=np.float32)
        self.specular = np.array(specular, dtype=np.float32)
        self.attenuation = np.array(attenuation, dtype=np.float32)
        self.enabled = True
        self.moving = False
        self.angle = 0.0
        self.orbital_speed = 0.5
        self.pulse_phase = 0.0
        self.quantum_effects_active = False

    def update(self, dt: float) -> None:
       
        if self.moving and self.quantum_effects_active:
            self.angle += dt * self.orbital_speed
            radius = np.linalg.norm(self.position[:3])
            self.position[0] = radius * np.cos(self.angle)
            self.position[2] = radius * np.sin(self.angle)
            
            # Add pulsing effect
            self.pulse_phase += dt * 2.0
            pulse_factor = 0.3 * np.sin(self.pulse_phase) + 1.0
            self.diffuse = self.diffuse * pulse_factor

    def setup(self, light_index: int) -> None:
       
        light = GL_LIGHT0 + light_index
        if self.enabled:
            glEnable(light)
            glLightfv(light, GL_POSITION, self.position)
            glLightfv(light, GL_AMBIENT, self.ambient)
            glLightfv(light, GL_DIFFUSE, self.diffuse)
            glLightfv(light, GL_SPECULAR, self.specular)
            glLightf(light, GL_CONSTANT_ATTENUATION, self.attenuation[0])
            glLightf(light, GL_LINEAR_ATTENUATION, self.attenuation[1])
            glLightf(light, GL_QUADRATIC_ATTENUATION, self.attenuation[2])
            
            # Add spotlight effect
            glLightf(light, GL_SPOT_CUTOFF, 45.0)
            glLightf(light, GL_SPOT_EXPONENT, 2.0)
            spot_direction = -self.position[:3]
            spot_direction = spot_direction / np.linalg.norm(spot_direction)
            glLightfv(light, GL_SPOT_DIRECTION, (*spot_direction, 1.0))
        else:
            glDisable(light)
class Particle:
    def __init__(self, x, y, z, velocity, particle_type):
       
        # Core properties
        self.position = np.array([x, y, z], dtype=np.float32)
        self.velocity = velocity
        self.particle_type = particle_type
        self.lifetime: float = 0.0
        self.max_lifetime: float = 15.0
        self.energy: float = 1.0
        self.phase = 0.0
        self.spin = np.random.choice([-0.5, 0.5])
        
        # Type-specific properties
        if particle_type == "electron":
            self.size = 0.6  # Increased size
            base_color = (0.4, 0.4, 1.0)
        elif particle_type == "plasma":
            self.size = 0.7
            base_color = (1.0, 0.4, 0.4)
        else:  # light
            self.size = 0.5
            base_color = (1.0, 1.0, 0.3)
            
        # Material properties
        self.material = Material(
            ambient=(0.3 * base_color[0], 0.3 * base_color[1], 0.3 * base_color[2], 1.0),
            diffuse=base_color,
            specular=(1.0, 1.0, 1.0, 1.0),
            emission=(1.2 * base_color[0], 1.2 * base_color[1], 1.2 * base_color[2], 1.0),
            shininess=64.0
        )
        # Quantum properties
        self.quantum_state = False
        self.interaction_strength = 0.0
        self.wave_packet_size = np.random.uniform(0.5, 1.0)
        self.trail_length = 30
        
        if particle_type == "electron":
            self.base_speed = 5.0  # Electron speed
            self.size = 0.6
        elif particle_type == "plasma":
            self.base_speed = 3.0  # Plasma speed (slower than electrons)
            self.size = 0.7
        else:  # light
            self.base_speed = 8.0  # Light speed (faster than electrons)
            self.size = 0.5
            
        # Scale initial velocity by base speed
        self.velocity = velocity * self.base_speed
        
        # Add quantum state tracking
        self.quantum_active = False
        self.quantum_effects = {
            'tunneling': False,
            'interference': False,
            'entanglement': False,
            'superposition': False
        }

    def update(self, dt, quantum_dot_pos):
       
        distance = np.linalg.norm(quantum_dot_pos - self.position)
        self.lifetime += dt
        self.phase += dt * 5.0  # Wave function phase
        
        if self.lifetime > self.max_lifetime:
            self.energy *= 0.98  # Slower energy decay
        
            # Quantum tunneling probability

            if distance > 0:
                tunnel_prob = np.exp(-distance / 5.0)
                
                if np.random.random() < tunnel_prob * 0.1:  # Reduced probability
                    self.quantum_effects['tunneling'] = True
                    # Tunneling effect
                    self.position += (quantum_dot_pos - self.position) * 0.1
                else:
                    self.quantum_effects['tunneling'] = False
                    
                # Quantum interference
                interference = np.cos(distance * 2.0 - self.phase)
                self.velocity += self.velocity * interference * 0.01
                self.quantum_effects['interference'] = abs(interference) > 0.5
                    
                if np.random.random() < 0.01:
                    self.quantum_effects['superposition'] = True
                    alt_velocity = np.random.normal(0, 1, 3)
                    self.velocity = (self.velocity + alt_velocity) * 0.5
                else:
                    self.quantum_effects['superposition'] = False
                    
            # Quantum force with spin interaction
        force = (quantum_dot_pos - self.position) / (distance ** 2)
        force *= (1.0 + 0.5 * np.sin(self.phase))  # Wave-like modulation
        force *= (1.0 + 0.2 * self.spin)  # Spin-dependent interaction
            
        interference = np.cos(distance * 2.0 - self.phase)
        self.velocity += self.velocity * interference * 0.01
        self.quantum_effects['interference'] = abs(interference) > 0.5
            # Apply quantum forces with velocity verlet integration
        self.velocity += force * dt
        self.velocity *= 0.99  # Slight damping
        
        # Update position with quantum uncertainty
        uncertainty = np.random.normal(0, 0.01, 3)  # Heisenberg uncertainty
        self.position += self.velocity * dt + uncertainty

        if self.lifetime > self.max_lifetime:
            self.energy *= 0.995
        
    def draw(self) -> None:
       
        glPushMatrix()
        glTranslatef(*self.position)
        
        # Scale emission based on energy and phase
        emission_scale = (1.0 + 0.3 * np.sin(self.phase)) * self.energy
        self.material.emission = tuple(e * emission_scale for e in self.material.emission)
        self.material.apply()
        
        # Draw particle core
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        
        # Size varies with wave packet
        size = 0.3 * (1.0 + 0.2 * np.sin(self.phase)) * self.wave_packet_size
        gluSphere(quad, size, 16, 16)
        
        # Draw quantum effects
        self._draw_wave_function()
        if self.particle_type == "electron":
            self._draw_spin_indicator()
        
        glPopMatrix()

    def _draw_wave_function(self) -> None:
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Enhanced wave function visualization
        glPointSize(4.0)  # Larger points
        glBegin(GL_POINTS)
        num_points = 120  # More points for smoother visualization
        for i in range(num_points):
            angle = i * (2 * np.pi / num_points)
            radius = self.wave_packet_size * (1.0 + 0.6 * np.sin(angle * 4 + self.phase))
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Enhanced probability density
            probability = np.exp(-(x**2 + y**2) / (2 * self.wave_packet_size**2))
            alpha = probability * 0.9 * self.energy  # Increased opacity
            
            if self.particle_type == "electron":
                intensity = 0.8 + 0.4 * np.sin(self.phase * 3.0)
                glColor4f(intensity * 0.4, intensity * 0.4, 1.0, alpha)
            elif self.particle_type == "plasma":
                glColor4f(1.0, 0.4, 0.4, alpha)
            else:  # light
                glColor4f(1.0, 1.0, 0.3, alpha)
                
            glVertex3f(x, y, 0)
        glEnd()
        
        # Add interference patterns
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        for i in range(72):
            angle = i * (2 * np.pi / 72)
            radius = self.size * 4.0 * (1.0 + 0.7 * np.sin(angle * 3 + self.phase))
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            alpha = 0.8 * np.exp(-radius / (self.size * 5.0))
            glColor4f(0.6, 0.6, 1.0, alpha)
            glVertex3f(x, y, 0)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)

    def _draw_spin_indicator(self) -> None:
       
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        
        # Draw spin arrow
        glBegin(GL_LINES)
        if self.spin > 0:
            glColor3f(0.3, 1.0, 0.3)
        else:
            glColor3f(1.0, 0.3, 0.3)
            
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0.5 * np.sign(self.spin), 0)
        glEnd()
        
        glEnable(GL_LIGHTING)

    def draw(self) -> None:
       
        glPushMatrix()
        glTranslatef(*self.position)
        
        if self.quantum_state:
            # Enhanced quantum glow
            quantum_factor = 3.0 + 2.0 * np.sin(self.phase * 2.0)
            interaction_boost = 1.0 + 3.0 * self.interaction_strength
            emission = list(self.material.emission)
            for i in range(3):
                emission[i] *= quantum_factor * interaction_boost
            self.material.emission = tuple(emission)
            
            # Larger size variations
            size = self.size * (1.0 + 0.8 * np.sin(self.phase))
        else:
            size = self.size
            
        self.material.apply()
        
        # Higher resolution sphere
        quad = gluNewQuadric()
        gluQuadricNormals(quad, GLU_SMOOTH)
        gluSphere(quad, size, 32, 32)
        
        if self.quantum_state:
            self._draw_enhanced_quantum_effects()
            self._draw_enhanced_trail()
        
        glPopMatrix()

    def _draw_enhanced_quantum_effects(self) -> None:
       
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Enhanced wave function visualization
        glPointSize(4.0)
        glBegin(GL_POINTS)
        num_points = 120
        for i in range(num_points):
            angle = i * (2 * np.pi / num_points)
            radius = self.wave_packet_size * (1.0 + 0.6 * np.sin(angle * 4 + self.phase))
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            probability = np.exp(-(x**2 + y**2) / (2 * self.wave_packet_size**2))
            alpha = probability * 0.9
            
            if self.particle_type == "electron":
                intensity = 0.8 + 0.4 * np.sin(self.phase * 3.0)
                glColor4f(intensity * 0.4, intensity * 0.4, 1.0, alpha)
            elif self.particle_type == "plasma":
                glColor4f(1.0, 0.4, 0.4, alpha)
            else:
                glColor4f(1.0, 1.0, 0.3, alpha)
                
            glVertex3f(x, y, 0)
        glEnd()
        
        # Draw interference patterns
        glLineWidth(2.0)
        glBegin(GL_LINE_STRIP)
        for i in range(72):
                angle = i * (2 * np.pi / 72)
                radius = self.size * 4.0 * (1.0 + 0.7 * np.sin(angle * 3 + self.phase))
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
            
                alpha = 0.8 * np.exp(-radius / (self.size * 5.0))
                glColor4f(0.6, 0.6, 1.0, alpha)
                glVertex3f(x, y, 0)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)

    def _draw_enhanced_trail(self) -> None:
      
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glLineWidth(3.0)
        
        glBegin(GL_LINE_STRIP)
        for i in range(self.trail_length):
            t = i / self.trail_length
            offset = self.velocity * t * -1.0
            alpha = 0.7 * (1.0 - t)
            
            if self.particle_type == "electron":
                glColor4f(0.4, 0.4, 1.0, alpha)
            elif self.particle_type == "plasma":
                glColor4f(1.0, 0.4, 0.4, alpha)
            else:
                glColor4f(1.0, 1.0, 0.3, alpha)
                
            pos = self.position + offset
            glVertex3f(*pos)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)
class QuantumDot:
   
    def __init__(self, x: float, y: float, z: float, radius: float):
       
        self.position = np.array([x, y, z], dtype=np.float32)
        self.radius = radius
        self.material = Material(
            ambient=(0.3, 0.2, 0.0, 1.0),
            diffuse=(1.0, 0.8, 0.0, 1.0),
            specular=(1.0, 1.0, 0.0, 1.0),
            emission=(0.5, 0.3, 0.0, 1.0),
            shininess=32.0
        )
        
        # Quantum mechanical properties
        self.energy_levels = np.array([1, 2, 3, 4, 5]) * 1.5
        self.occupied_levels = np.zeros_like(self.energy_levels, dtype=bool)
        self.excitation = 0.0
        self.orbital_rotation = 0.0
        self.coherence_time = 10.0
        self.decoherence_factor = 1.0
        self.entangled_particles = []
        
        # Initialize quantum state
        self.wave_function = self._initialize_wave_function()
        self.electron_density = self._calculate_electron_density()
        self.generate_probability_cloud()

    def _calculate_electron_density(self) -> np.ndarray:
      
        r = np.linspace(0, self.radius * 3, 100)
        density = np.zeros_like(r)
        
        for n in range(1, 4):
            # Quantum mechanical radial wave function
            psi = np.sqrt(2.0 / (n * self.radius)) * np.exp(-r / (n * self.radius))
            # Add quantum oscillations
            psi *= np.cos(2 * np.pi * r / (n * self.radius))
            density += np.abs(psi) ** 2
            
        return density

    def _initialize_wave_function(self) -> Dict[str, np.ndarray]:
        
        theta = np.linspace(0, np.pi, 50)
        phi = np.linspace(0, 2 * np.pi, 50)
        
        return {
            'ground_state': np.outer(np.sin(theta), np.cos(phi)),
            'excited_state': np.outer(np.sin(2 * theta), np.cos(2 * phi)),
            'superposition': 0.707 * (np.outer(np.sin(theta), np.cos(phi)) + 
                                    np.outer(np.sin(2 * theta), np.cos(2 * phi)))
        }

    def generate_probability_cloud(self) -> None:
      
        self.electron_probability_cloud = []
        n_points = 2000  # Increased number of points
        
        for _ in range(n_points):
            # Quantum mechanical probability distribution
            r = np.random.exponential(2.0) * self.radius
            theta = np.arccos(np.random.uniform(-1, 1))
            phi = np.random.uniform(0, 2 * np.pi)
            
            # Apply quantum interference effects
            interference = np.cos(r * 5.0) ** 2  # Interference pattern
            if np.random.random() < interference:
                x = r * np.sin(theta) * np.cos(phi)
                y = r * np.sin(theta) * np.sin(phi)
                z = r * np.cos(theta)
                self.electron_probability_cloud.append(np.array([x, y, z]))

    def update(self, dt: float, particles: List[Particle]) -> None:
        
        # Natural quantum decoherence
        self.decoherence_factor *= np.exp(-dt / self.coherence_time)
        self.excitation *= np.exp(-dt / 5.0)  # Quantum state decay
        
        # Update orbital rotation with quantum phase
        self.orbital_rotation += dt * (0.5 + 0.3 * np.sin(dt * 2.0))
        
        # Particle interactions
        for particle in particles:
            distance = np.linalg.norm(particle.position - self.position)
            if distance < self.radius * 3:
                # Enhanced quantum tunneling
                tunneling_prob = np.exp(-distance / self.radius) * (1.0 + 0.2 * np.sin(particle.phase))
                self.excitation += tunneling_prob * 0.2
                
                # Quantum entanglement effects
# Quantum entanglement effects
                if particle not in self.entangled_particles and np.random.random() < 0.1:
                    self.entangled_particles.append(particle)
                    particle.velocity *= -1  # Quantum state transfer
                
                if particle.particle_type == "electron":
                    # Electron capture with quantum tunneling
                    if distance < self.radius * 1.5 and np.random.random() < 0.1:
                        self._handle_electron_capture(particle)

        # Update entangled particles
        self.entangled_particles = [p for p in self.entangled_particles if p in particles]
        
        # Regenerate probability cloud periodically
        if np.random.random() < 0.05:
            self.generate_probability_cloud()

    def _handle_electron_capture(self, particle: Particle) -> None:

        # Find available energy level
        for i, occupied in enumerate(self.occupied_levels):
            if not occupied:
                self.occupied_levels[i] = True
                # Quantum excitation with energy conservation
                excitation_energy = particle.energy * (1.0 - np.exp(-particle.lifetime / 5.0))
                self.excitation += excitation_energy
                particle.energy *= (1.0 - excitation_energy)
                break

    def draw(self) -> None:
       
        try:
            glPushMatrix()  # Main transform
            glTranslatef(*self.position)
            
            # Calculate emission intensity based on excitation
            emission_scale = np.clip(1.0 + 0.5 * self.excitation * self.decoherence_factor, 0.0, 2.0)
            base_emission = list(self.material.emission)
            safe_emission = [float(np.clip(e * emission_scale, 0.0, 1.0)) for e in base_emission]
            
            # Ensure material has all components
            glMaterialfv(GL_FRONT, GL_AMBIENT, self.material.ambient)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, self.material.diffuse)
            glMaterialfv(GL_FRONT, GL_SPECULAR, self.material.specular)
            glMaterialfv(GL_FRONT, GL_EMISSION, safe_emission)
            glMaterialf(GL_FRONT, GL_SHININESS, self.material.shininess)
            
            # Draw core sphere
            self._draw_core()
            
            # Draw quantum effects only if excited and effects are enabled
            if self.excitation > 0.1 and self.decoherence_factor > 0.5:
                self._draw_probability_cloud()
                self._draw_energy_levels()
            
            glPopMatrix()  # End main transform
            
        except GLError as e:
            print(f"OpenGL Error in quantum dot drawing: {e}")
            # Clean up matrix stack
            glPopMatrix()
            glLoadIdentity()

    def _draw_core(self) -> None:
        """Draw core sphere safely"""
        try:
            quad = gluNewQuadric()
            if quad:
                gluQuadricNormals(quad, GLU_SMOOTH)
                gluSphere(quad, self.radius, 32, 32)
                gluDeleteQuadric(quad)
        except GLError as e:
            print(f"OpenGL Error in core drawing: {e}")
            
    def _draw_probability_cloud(self) -> None:
    
        try:
            glPushMatrix()
            
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            glPointSize(2.0)
            
            # Apply quantum rotation
            rot_matrix = R.from_euler('y', self.orbital_rotation).as_matrix()
            
            glBegin(GL_POINTS)
            for point in self.electron_probability_cloud:
                # Apply quantum interference pattern
                rotated_point = rot_matrix @ point
                distance = np.linalg.norm(rotated_point)
                
                # Calculate quantum effects
                interference = np.cos(distance * 5.0 - self.orbital_rotation) ** 2
                wave_factor = np.sin(distance * 2.0 - self.orbital_rotation)
                
                # Controlled alpha value
                alpha = 0.3 * self.excitation * interference * self.decoherence_factor
                alpha = np.clip(alpha, 0.0, 0.5)  # Limit maximum alpha
                
                # Use golden color with controlled intensity
                color = np.array([1.0, 0.8, 0.0]) * (0.5 + 0.5 * wave_factor)
                glColor4f(*color, alpha)
                glVertex3f(*rotated_point)
            glEnd()
            
            glEnable(GL_LIGHTING)
            glPopMatrix()
            
        except GLError as e:
            print(f"OpenGL Error in probability cloud: {e}")
            glEnable(GL_LIGHTING)
            glPopMatrix()

    def _draw_energy_levels(self) -> None:
       
        try:
            # Setup drawing state
            glPushMatrix()
            
            # Store lighting state only when needed
            lighting_enabled = glIsEnabled(GL_LIGHTING)
            glDisable(GL_LIGHTING)
            
            # Draw energy levels
            glLineWidth(2.0)
            glBegin(GL_LINES)
            for i, energy in enumerate(self.energy_levels):
                # Color gradient based on energy level
                color = (0.2, 0.5 + 0.5 * (i / len(self.energy_levels)), 1.0)
                glColor3fv(color)
                
                # Draw horizontal line
                x_offset = 2.0
                glVertex3f(-x_offset, energy, 0.0)
                glVertex3f(x_offset, energy, 0.0)
            glEnd()
            
        except GLError as e:
            print(f"OpenGL Error: {e}")
            
        finally:
            # Restore states
            glLineWidth(1.0)  # Reset to default
            glPopMatrix()
            if lighting_enabled:
                glEnable(GL_LIGHTING)
    
    def _draw_level_labels(self):
        """Draw labels for energy levels"""
        for i, energy in enumerate(self.energy_levels):
            # Implementation for drawing text labels
            pass
class LightBeam:
    def __init__(self, position: np.ndarray, direction: np.ndarray, wavelength: float = 550):
        self.position = position.astype(np.float32)
        self.direction = direction / np.linalg.norm(direction)
        self.length = 20.0
        self.wavelength = wavelength
        self.intensity = 1.0
        self.phase = 0.0
        self.width = 0.2
        self.photon_count = 50
        self.photon_positions = []
        self.interference_pattern = []
        self.generate_photons()
        self.generate_interference()
        
    def generate_photons(self):
        """Generate quantum photon positions along the beam"""
        self.photon_positions = []
        for _ in range(self.photon_count):
            # Random position along beam with quantum uncertainty
            distance = np.random.uniform(0, self.length)
            uncertainty = np.random.normal(0, 0.1, 3)
            pos = self.position + self.direction * distance
            pos += np.cross(self.direction, [0, 1, 0]) * uncertainty[0]
            pos += np.cross(self.direction, np.cross(self.direction, [0, 1, 0])) * uncertainty[1]
            self.photon_positions.append(pos)
            
    def generate_interference(self):
        """Generate quantum interference pattern"""
        points = 50
        self.interference_pattern = []
        for i in range(points):
            x = i / points * self.length
            # Complex quantum interference calculation
            amplitude = np.cos(2 * np.pi * x / (self.wavelength * 0.001))
            amplitude *= np.exp(-x / (self.length * 0.5))
            self.interference_pattern.append(abs(amplitude))
            
    def update(self, dt: float):
        # Update quantum phase
        self.phase += dt * 5.0
        if self.phase > 2 * np.pi:
            self.phase -= 2 * np.pi
            
        # Update photon positions with quantum motion
        for i in range(len(self.photon_positions)):
            # Quantum uncertainty in position
            uncertainty = np.random.normal(0, 0.02, 3)
            self.photon_positions[i] += self.direction * dt * 5.0
            self.photon_positions[i] += uncertainty
            
            # Reset photons that reach the end
            if np.dot(self.photon_positions[i] - self.position, self.direction) > self.length:
                self.photon_positions[i] = self.position + uncertainty
                
        # Update interference pattern
        if np.random.random() < 0.1:  # Occasional updates
            self.generate_interference()
            
    def draw(self):
        """Draw the light beam with quantum effects"""
        try:
            glPushMatrix()
            
            # Draw main beam
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            
            # Convert wavelength to RGB (simplified)
            if self.wavelength < 450:
                color = (0.5, 0.5, 1.0)  # Blue
            elif self.wavelength < 550:
                color = (0.0, 1.0, 0.0)  # Green
            else:
                color = (1.0, 0.0, 0.0)  # Red
                
            # Draw beam core with interference pattern
            glBegin(GL_QUAD_STRIP)
            for i, amplitude in enumerate(self.interference_pattern):
                t = i / len(self.interference_pattern)
                pos = self.position + self.direction * (t * self.length)
                width_vector = np.cross(self.direction, [0, 1, 0])
                width_vector = width_vector / np.linalg.norm(width_vector) * self.width
                
                alpha = 0.3 * amplitude * self.intensity
                glColor4f(*color, alpha)
                glVertex3f(*(pos + width_vector))
                glVertex3f(*(pos - width_vector))
            glEnd()
            
            # Draw quantum photons
            glPointSize(3.0)
            glBegin(GL_POINTS)
            for pos in self.photon_positions:
                intensity = 0.8 + 0.2 * np.sin(self.phase)
                glColor4f(*color, intensity * 0.5)
                glVertex3f(*pos)
            glEnd()
            
            glEnable(GL_LIGHTING)
            glPopMatrix()
            
        except GLError as e:
            print(f"OpenGL Error in light beam drawing: {e}")
            glEnable(GL_LIGHTING)
            glPopMatrix()
class ParticleManager:
    def __init__(self):
        self.particles = []
        self.particles_to_remove = set()
    
    def add_particle(self, x, y, z, velocity, particle_type):
        """Create and add a new particle"""
        particle = Particle(x, y, z, velocity, particle_type)
        self.particles.append(particle)
        return particle
        
    def remove_particle(self, particle):
        """Mark a particle for removal"""
        self.particles_to_remove.add(particle)
        
    def clean_up(self):
        """Remove all marked particles"""
        if self.particles_to_remove:
            self.particles = [p for p in self.particles if p not in self.particles_to_remove]
            self.particles_to_remove.clear()
            
    def update(self, dt, quantum_dot_pos):
        """Update all particles and handle removals"""
        for particle in self.particles:
            particle.update(dt, quantum_dot_pos)
            
            # Check if particle should be removed
            if particle.lifetime > particle.max_lifetime and particle.energy < 0.1:
                self.remove_particle(particle)
        
        self.clean_up()
        
    def draw(self):
        """Draw all active particles"""
        for particle in self.particles:
            particle.draw()
            
    def get_count(self):
        """Get current number of active particles"""
        return len(self.particles)
class SimulationBase(ABC):
    """
    SimulationBase is an abstract base class for a quantum dot simulation using Pygame and OpenGL.
    Attributes:
        width (int): Width of the display window.
        height (int): Height of the display window.
        display (pygame.Surface): Pygame display surface with OpenGL context.
        camera_distance (float): Distance of the camera from the origin.
        camera_rotation (List[float]): Rotation angles of the camera.
        mouse_pressed (bool): State of the mouse button (pressed or not).
        prev_mouse_pos (Tuple[int, int]): Previous mouse position.
        running (bool): State of the simulation loop (running or not).
        paused (bool): State of the simulation (paused or not).
        particles (List[Particle]): List of particles in the simulation.
        quantum_dot (QuantumDot): Quantum dot object in the simulation.
        lights (List[Light]): List of light sources in the simulation.
        clock (pygame.time.Clock): Pygame clock for timing.
    Methods:
        __init__(width: int = 1024, height: int = 768) -> None:
            Initializes the simulation with display properties, camera properties, input state, physics objects, and timing.
        _handle_keypress(key: int) -> None:
            Handles keyboard input with enhanced controls.
        _add_particle(particle_type: str) -> None:
            Abstract method to add a particle to the simulation. Must be implemented by subclasses.
        update(dt: float) -> None:
            Updates the simulation state with enhanced quantum effects. If the simulation is not paused, updates the state of the lights, particles, and quantum dot.
        draw() -> None:
            Renders the scene with enhanced effects, including the coordinate system, quantum dot, and particles.
        _draw_axes() -> None:
            Draws the enhanced coordinate system axes.
        run() -> None:
            Main simulation loop with consistent timing. Handles events, updates the simulation state, and renders the scene.
        """
    def __init__(self, width: int = 1024, height: int = 768) -> None:
      
        pygame.init()
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        
        # Timing
        self.clock = pygame.time.Clock()
        
        # Display setup
        self.display = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | HWSURFACE)
        self.width = width
        self.height = height
        
        # Camera properties - Add these before other initializations
        self.camera_distance = 40.0
        self.camera_rotation = [30.0, 0.0]
        
        # Simulation state
        self.running = True
        self.paused = False
        
        # Input state
        self.mouse_pressed = False
        self.prev_mouse_pos = (0, 0)
        
        # Physics objects
        self.particles = []
        self.quantum_dot = QuantumDot(0, 0, 0, 2.0)
        self.lights = [
            Light((50.0, 50.0, 50.0, 1.0),
                 (0.4, 0.4, 0.4, 1.0),
                 (1.0, 1.0, 1.0, 1.0),
                 (1.0, 1.0, 1.0, 1.0)),
            Light((-30.0, -30.0, 50.0, 1.0),
                 (0.2, 0.2, 0.2, 1.0),
                 (0.8, 0.8, 1.0, 1.0),
                 (0.8, 0.8, 1.0, 1.0))
        ]

        self.quantum_effects_enabled = False
        self.quantum_effects_timer = 0
        self.particle_lifetime = 45.0  # Increased particle lifetime
        
        # Initialize OpenGL
        self.init_gl()

    def init_gl(self) -> None:
        """Initialize OpenGL settings."""
        glClearColor(0.05, 0.05, 0.1, 1.0)
        glViewport(0, 0, self.width, self.height)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_BLEND)
        glEnable(GL_MULTISAMPLE)
        
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
        

    def _handle_keypress(self, key: int) -> None:
        if key == pygame.K_q:
            self.quantum_effects_enabled = not self.quantum_effects_enabled
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.paused = not self.paused
            for particle in self.particles:
                particle.quantum_active = self.quantum_effects_enabled
        elif key == pygame.K_q:
            # Toggle quantum effects instead of quitting
            self.quantum_dot.decoherence_factor = 1.0 if self.quantum_dot.decoherence_factor < 0.5 else 0.0
            print(f"Quantum effects: {'enabled' if self.quantum_dot.decoherence_factor > 0.5 else 'disabled'}")
        elif key == pygame.K_e:
            self._add_particle("electron")
            print("Added electron particle")
        elif key == pygame.K_p:
            self._add_particle("plasma")
            print("Added plasma particle")
            if self.quantum_effects_enabled:
                print("\nQuantum Effects Enabled:")
                print("- Quantum Tunneling")
                print("- Wave-Particle Duality")
                print("- Quantum Interference")
                print("- Quantum Superposition")
                print("- Quantum Entanglement")
            else:
                print("\nQuantum Effects Disabled")
        elif key == pygame.K_c:
            self.particles.clear()
            self.quantum_dot.entangled_particles.clear()
        elif key == pygame.K_r:
            self.camera_rotation = [30.0, 0.0]
            self.camera_distance = 40.0
        elif key == pygame.K_q:
            # Toggle quantum effects visibility
            self.quantum_dot.decoherence_factor = 1.0 if self.quantum_dot.decoherence_factor < 0.5 else 0.0

    @abstractmethod
    def _add_particle(self, particle_type: str) -> None:
        """Add a particle to the simulation."""
        pass

    def update(self, dt: float) -> None:
        if not self.paused:
            # Update lights
            for light in self.lights:
                light.update(dt)
            
            # Create a list of particles to remove
            particles_to_remove = set()
            
            # Update particles with quantum effects
            for particle in self.particles[:]:  # Create a copy for safe iteration
                particle.update(dt, self.quantum_dot.position)
                
                # Check removal conditions
                if (particle.energy < 0.1 or 
                    np.linalg.norm(particle.position) > 100 or 
                    particle.lifetime > self.particle_lifetime):
                    
                    # Mark for removal instead of immediate removal
                    particles_to_remove.add(particle)
            
            # Clean up entangled particles
            self.quantum_dot.entangled_particles = [
                p for p in self.quantum_dot.entangled_particles 
                if p in self.particles and p not in particles_to_remove
            ]
            
            # Remove marked particles
            self.particles = [
                p for p in self.particles 
                if p not in particles_to_remove
            ]
            
            # Update quantum dot
            self.quantum_dot.update(dt, self.particles)
    def draw(self) -> None:
       
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Camera setup
        glTranslatef(0, 0, -self.camera_distance)
        glRotatef(self.camera_rotation[0], 1, 0, 0)
        glRotatef(self.camera_rotation[1], 0, 1, 0)
        
        # Setup lights
        for i, light in enumerate(self.lights):
            light.setup(i)
        
        # Draw coordinate system
        self._draw_axes()
        
        # Draw quantum dot and particles with proper matrix management
        try:
            glPushMatrix()  # Push matrix for quantum dot
            self.quantum_dot.draw()
            glPopMatrix()   # Pop matrix after quantum dot
            
            glPushMatrix()  # Push matrix for particles
            glEnable(GL_BLEND)
            for particle in self.particles:
                particle.draw()
            glPopMatrix()   # Pop matrix after particles
            
        except GLError as e:
            print(f"Caught OpenGL Error: {e}")
            # Ensure we're in a good state
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
        
        pygame.display.flip()

    def _draw_axes(self) -> None:
        """Draw coordinate system axes."""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        
        glBegin(GL_LINES)
        # X axis (red)
        glColor3f(1, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(10, 0, 0)
        # Y axis (green)
        glColor3f(0, 1, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 10, 0)
        # Z axis (blue)
        glColor3f(0, 0, 1)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, 10)
        glEnd()
        
        glEnable(GL_LIGHTING)

    def run(self) -> None:
        
        fixed_dt = 1.0 / 60.0  # Fixed time step
        accumulated_time = 0.0
        
        try:
            while self.running:
                if not self.handle_events():
                    break
                    
                frame_time = self.clock.tick(60) / 1000.0
                accumulated_time += frame_time
                
                # Update with fixed time step
                while accumulated_time >= fixed_dt:
                    self.update(fixed_dt)
                    accumulated_time -= fixed_dt
                
                self.draw()
                
        finally:
            pygame.quit()

    def handle_events(self) -> bool:
      
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
        
            elif event.type == pygame.KEYDOWN:
                key: int = event.key
                if key == pygame.K_ESCAPE:
                    print("Exiting simulation...")
                    self.running = False
                    return False
                elif key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif key == pygame.K_q:
                    # Toggle quantum effects
                    self.quantum_dot.decoherence_factor = 1.0 if self.quantum_dot.decoherence_factor < 0.5 else 0.0
                    print(f"Quantum effects: {'enabled' if self.quantum_dot.decoherence_factor > 0.5 else 'disabled'}")
                elif key == pygame.K_e:
                    self._add_particle("electron")
                    print("Added electron particle")
                elif key == pygame.K_p:
                    self._add_particle("plasma")
                    print("Added plasma particle")
                elif key == pygame.K_c:
                    self.particles.clear()
                    self.quantum_dot.entangled_particles.clear()
                elif key == pygame.K_r:
                    self.camera_rotation = [30.0, 0.0]
                    self.camera_distance = 40.0
        
            elif event.type == MOUSEBUTTONDOWN:
                button: int = event.button
                pos: Tuple[int, int] = event.pos
                if button in (1, 3):  # Left or right mouse button
                    self.mouse_pressed = True
                    self.prev_mouse_pos = pos
                elif button == 4:  # Mouse wheel up
                    self.camera_distance = max(5.0, self.camera_distance - 1.0)
                elif button == 5:  # Mouse wheel down
                    self.camera_distance = min(100.0, self.camera_distance + 1.0)
        
            elif event.type == MOUSEBUTTONUP:
                button: int = event.button
                if button in (1, 3):
                    self.mouse_pressed = False
        
            elif event.type == MOUSEMOTION and self.mouse_pressed:
                pos: Tuple[int, int] = event.pos
                dx: float = pos[0] - self.prev_mouse_pos[0]
                dy: float = pos[1] - self.prev_mouse_pos[1]
                self.camera_rotation[1] += dx * 0.5
                self.camera_rotation[0] = max(-90, min(90, self.camera_rotation[0] + dy * 0.5))
                self.prev_mouse_pos = pos
    
        return True
class ElectronSimulation(SimulationBase):
   
    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        pygame.display.set_caption("Quantum Dot - Electron Interaction")
        self._initialize_particles()

    def _initialize_particles(self) -> None:
      
        for _ in range(15):
            # Generate positions on a quantum orbital shell
            phi = np.random.uniform(0, 2 * np.pi)
            theta = np.arccos(np.random.uniform(-1, 1))
            # Multiple orbital shells
            r = np.random.choice([10, 20, 30]) + np.random.uniform(-2, 2)
            
            pos = np.array([
                r * np.sin(theta) * np.cos(phi),
                r * np.sin(theta) * np.sin(phi),
                r * np.cos(theta)
            ])
            
            # Calculate quantum mechanical velocity
            orbital_velocity = np.cross(pos, np.array([0, 1, 0]))
            orbital_velocity = 0.3 * orbital_velocity / np.linalg.norm(orbital_velocity)
            
            # Add quantum uncertainty to velocity
            uncertainty = np.random.normal(0, 0.05, 3)
            vel = orbital_velocity + uncertainty
            
            self.particles.append(Particle(*pos, vel, "electron"))

    def _add_particle(self, particle_type: str) -> None:
     
        if particle_type != "electron":
            return
        
        try:
            # Generate position farther from center for better visibility
            phi = np.random.uniform(0, 2 * np.pi)
            theta = np.arccos(np.random.uniform(-1, 1))
            r = np.random.uniform(5, 15)  # Reduced distance range for better visibility
            
            # Calculate position with quantum uncertainty
            pos = np.array([
                r * np.sin(theta) * np.cos(phi),
                r * np.sin(theta) * np.sin(phi),
                r * np.cos(theta)
            ])
            
            # Calculate velocity for more visible motion
            orbital_velocity = np.cross(pos, np.array([0, 1, 0]))
            velocity = orbital_velocity / np.linalg.norm(orbital_velocity)
            velocity *= 2.0  # Increased velocity for better visibility
            
            # Create and add particle
            particle = Particle(*pos, velocity, "electron")
            particle.size = 0.5  # Increased size for better visibility
            self.particles.append(particle)
            
            print(f"Added electron at position {pos}")
            
        except Exception as e:
            print(f"Error creating electron particle: {e}")        
class PlasmaSimulation(SimulationBase):
   
    def __init__(self, width: int = 800, height: int = 600):

        super().__init__(width, height)
        pygame.display.set_caption("Quantum Dot - Plasma Interaction")
        self._initialize_particles()

    def _initialize_particles(self) -> None:

        for _ in range(25):
            # Generate positions in a quantum toroidal configuration
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(15, 25)
            R = 20  # Major radius
            
            # Add quantum fluctuations to position
            fluctuation = np.random.normal(0, 0.5, 3)
            pos = np.array([
                (R + r * np.cos(theta)) * np.cos(phi),
                (R + r * np.cos(theta)) * np.sin(phi),
                r * np.sin(theta)
            ]) + fluctuation
            
            # Calculate velocity with quantum effects
            base_vel = np.array([
                -np.sin(phi),
                np.cos(phi),
                0.1 * np.cos(theta)
            ])
            
            # Add quantum uncertainty to velocity
            uncertainty = np.random.normal(0, 0.05, 3)
            vel = 0.2 * base_vel / np.linalg.norm(base_vel) + uncertainty
            
            self.particles.append(Particle(*pos, vel, "plasma"))

    def _add_particle(self, particle_type: str) -> None:

        if particle_type != "plasma":
            return
            
        try:
            # Generate quantum toroidal parameters with better visibility
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(8, 15)  # Reduced radius for better visibility
            R = 12  # Reduced major radius
            
            # Position with controlled fluctuations
            fluctuation = np.random.normal(0, 0.2, 3)  # Reduced fluctuation
            pos = np.array([
                (R + r * np.cos(theta)) * np.cos(phi),
                (R + r * np.cos(theta)) * np.sin(phi),
                r * np.sin(theta)
            ]) + fluctuation
            
            # Velocity with increased magnitude for visibility
            base_vel = np.array([
                -np.sin(phi),
                np.cos(phi),
                0.2 * np.cos(theta)  # Increased z-component
            ])
            
            uncertainty = np.random.normal(0, 0.02, 3)  # Reduced uncertainty
            vel = 0.5 * base_vel / np.linalg.norm(base_vel) + uncertainty  # Increased velocity scale
            
            # Create particle with increased size
            particle = Particle(*pos, vel, "plasma")
            particle.size = 0.8  # Larger size for better visibility
            particle.color = (0.6, 0.2, 1.0, 0.8)  # Purple color for plasma
            
            self.particles.append(particle)
            print(f"Added plasma particle at position {pos}")
            
        except Exception as e:
            print(f"Error creating plasma particle: {e}")
class LightSimulation(SimulationBase):
    def __init__(self, width: int = 800, height: int = 600):
        super().__init__(width, height)
        self.quantum_visual_intensity = 1.0
        pygame.display.set_caption("Quantum Dot - Light Interaction")
        self.light_beams: List[LightBeam] = []
        self.quantum_effects_enabled = True
        self._initialize_beams()
        
    def _initialize_beams(self):
        """Initialize some default light beams"""
        # Add initial beams with different wavelengths
        self.light_beams.append(LightBeam(
            np.array([0, 0, 0]),
            np.array([1, 0.5, 0.3]),
            wavelength=450  # Blue
        ))
        self.light_beams.append(LightBeam(
            np.array([0, 0, 0]),
            np.array([-0.5, 1, 0.3]),
            wavelength=550  # Green
        ))
        
    def _add_light_beam(self):
        """Add a new light beam with random properties"""
        # Random position near the origin
        position = np.random.normal(0, 2, 3)
        
        # Random direction
        phi = np.random.uniform(0, 2 * np.pi)
        theta = np.arccos(np.random.uniform(-1, 1))
        direction = np.array([
            np.sin(theta) * np.cos(phi),
            np.sin(theta) * np.sin(phi),
            np.cos(theta)
        ])
        
        # Random wavelength (between blue and red)
        wavelength = np.random.uniform(400, 700)
        
        # Create and add the beam
        beam = LightBeam(position, direction, wavelength)
        self.light_beams.append(beam)
        print(f"Added light beam with wavelength {wavelength:.1f}nm")
        
    def _add_particle(self, particle_type: str): # Add particle
        """Override particle addition for light simulation"""
        if particle_type == "light":
            self._add_light_beam()
            
    def update(self, dt: float):
        """Update simulation state"""
        super().update(dt)

        if not self.paused:
            # Update quantum dot
            self.quantum_dot.update(dt, self.particles)
            
            # Update light beams
            for beam in self.light_beams:
                beam.update(dt)
                
            # Update any remaining particles
            for particle in self.particles[:]:
                particle.update(dt, self.quantum_dot.position)
                if particle.energy < 0.1 or np.linalg.norm(particle.position) > 100:
                    if particle in self.quantum_dot.entangled_particles:
                        self.quantum_dot.entangled_particles.remove(particle)
                    self.particles.remove(particle)
        if self.quantum_effects_enabled:
            # Update quantum visual intensity for light beams
            self.quantum_visual_intensity = 1.0 + 0.3 * np.sin(time.time() * 2.0)
            
            for beam in self.light_beams:
                beam.intensity = self.quantum_visual_intensity
                # Add quantum fluctuations to beam properties
                beam.width = 0.2 * (1.0 + 0.1 * np.sin(time.time() * 3.0))
                beam.phase += dt * 2.0
                    
    def draw(self):
        """Draw the simulation""" #draw light simulation
        super().draw()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Camera setup
        glTranslatef(0, 0, -self.camera_distance)
        glRotatef(self.camera_rotation[0], 1, 0, 0)
        glRotatef(self.camera_rotation[1], 0, 1, 0)
        
        # Setup lights
        for i, light in enumerate(self.lights):
            light.setup(i)
        
        # Draw coordinate system
        self._draw_axes()
        
        try:
            # Draw quantum dot
            glPushMatrix()
            self.quantum_dot.draw()
            glPopMatrix()
            
            # Draw light beams
            glPushMatrix()
            for beam in self.light_beams:
                beam.draw()
            glPopMatrix()
            
            # Draw particles
            glPushMatrix()
            glEnable(GL_BLEND)
            for particle in self.particles:
                particle.draw()
            glPopMatrix()
            
        except GLError as e:
            print(f"Caught OpenGL Error: {e}")
            glLoadIdentity()
        
        pygame.display.flip()

        if self.quantum_effects_enabled:
            # Add quantum interference patterns
            glPushMatrix()
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            
            for beam in self.light_beams:
                # Draw quantum interference patterns
                glBegin(GL_TRIANGLE_STRIP)
                num_points = 50
                for i in range(num_points):
                    t = i / (num_points - 1)
                    offset = np.sin(t * 10 + beam.phase) * 0.5
                    
                    # Calculate positions with quantum effects
                    pos1 = beam.position + beam.direction * (t * beam.length) + np.array([offset, 0, 0])
                    pos2 = beam.position + beam.direction * (t * beam.length) - np.array([offset, 0, 0])
                    
                    # Set colors based on wavelength and quantum intensity
                    alpha = (1.0 - t) * 0.3 * self.quantum_visual_intensity
                    if beam.wavelength < 450:
                        glColor4f(0.3, 0.3, 1.0, alpha)
                    elif beam.wavelength < 550:
                        glColor4f(0.3, 1.0, 0.3, alpha)
                    else:
                        glColor4f(1.0, 0.3, 0.3, alpha)
                        
                    glVertex3f(*pos1)
                    glVertex3f(*pos2)
                
                glEnd()
            
            glEnable(GL_LIGHTING)
            glDisable(GL_BLEND)
            glPopMatrix()
        
    def handle_events(self) -> bool: # Input events
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_l:
                    self._add_light_beam()
                elif event.key == pygame.K_q:
                    self.quantum_effects_enabled = not self.quantum_effects_enabled
                    for beam in self.light_beams:
                        beam.intensity = 1.0 if self.quantum_effects_enabled else 0.5
                elif event.key == pygame.K_c:
                    self.light_beams.clear()
                elif event.key == pygame.K_r:
                    self.camera_rotation = [30.0, 0.0]
                    self.camera_distance = 40.0
                    
            # Handle mouse events from parent class
            elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION):
                super().handle_events()
                
        return True
def display_controls():
    """Display simulation controls in the terminal."""
    print("\nQuantum Dot Simulation Controls")
    print("==============================")
    print("\nCamera Controls:")
    print("  Mouse Drag: Rotate view")
    print("  Mouse Wheel: Zoom in/out")
    print("  R: Reset camera view")
    print("\nParticle Controls:")
    print("  E: Add electron (Electron mode)")
    print("  P: Add plasma particle (Plasma mode)")
    print("  L: Add light beam (Light mode)")
    print("  C: Clear all particles/beams")
    print("\nSimulation Controls:")
    print("  Space: Pause/Resume simulation")
    print("  Q: Toggle quantum effects")
    print("  ESC: Exit simulation")
    print("\n==============================\n")
def run_simulation(sim_type: str = "electron", width: int = 1024, height: int = 768) -> None:
    """
Runs a quantum simulation of either electron or plasma behavior with advanced visualization.


This function initializes and executes a sophisticated quantum simulation using Pygame and OpenGL.
It demonstrates quantum mechanical effects including wave-particle duality, quantum tunneling,
spin interactions, and quantum entanglement through real-time visualization.


Args:
    sim_type (str, optional): Type of simulation to run. Options:
        - "electron": Simulates electron-quantum dot interactions with quantum tunneling,
                     spin effects, and orbital dynamics
                     
        - "plasma": Simulates plasma-quantum dot interactions with collective quantum
                   behaviors and toroidal confinement
                   
        Defaults to "electron".
       
    width (int, optional): Width of simulation window in pixels. Higher values provide
        better visualization detail but require more computational resources.
        Minimum recommended: 800px. Defaults to 1024px.
       
    height (int, optional): Height of simulation window in pixels. Higher values provide
        better visualization detail but require more computational resources.
        Minimum recommended: 600px. Defaults to 768px.


Technical Features:
    - Real-time 3D visualization using OpenGL
    - Quantum mechanical wave function visualization
    - Particle-wave duality effects
    - Quantum tunneling and barrier penetration
    - Spin-orbit coupling and quantum entanglement
    - Adaptive time-step integration for stability
    - Multi-sample anti-aliasing for smooth rendering
    - Dynamic lighting with quantum interference patterns


Performance Considerations:
    - GPU acceleration recommended for optimal performance
    - Memory usage scales with particle count
    - Frame rate may decrease with large particle numbers (>1000)
    - Window size affects rendering performance


Raises:
    ValueError: If sim_type is not one of ["electron", "plasma"]
    pygame.error: If Pygame initialization fails
    OpenGL.error: If OpenGL context creation fails
    MemoryError: If system resources are insufficient
    Exception: For other unexpected errors during simulation


Example Usage:
    >>> # Run electron simulation with default settings
    >>> run_simulation("electron")
   
    >>> # Run plasma simulation with custom window size
    >>> run_simulation("plasma", width=1920, height=1080)
   
    >>> # Run electron simulation with minimum window size
    >>> run_simulation("electron", width=800, height=600)
    """
    try:
        if sim_type.lower() == "electron":
            sim = ElectronSimulation(width=width, height=height)
        elif sim_type.lower() == "plasma":
            sim = PlasmaSimulation(width=width, height=height)
        elif sim_type.lower() == "light":
            sim = LightSimulation(width=width, height=height)
        else:
            raise ValueError("Invalid simulation type. Choose 'electron', 'plasma', or 'light'.")
        
        sim.run()
        
    except Exception as e:
        print(f"Error running simulation: {str(e)}")
        pygame.quit()
        raise
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantum Dot Simulation")
    parser.add_argument('--type', type=str, default="electron",
                       choices=['electron', 'plasma', 'light'],  # Added 'light' as valid choice
                       help='Type of simulation to run (electron, plasma, or light)')
    parser.add_argument('--width', type=int, default=1024,
                       help='Window width (default: 1024)')
    parser.add_argument('--height', type=int, default=768,
                       help='Window height (default: 768)')
    
    args = parser.parse_args()
    
    try:
        run_simulation(args.type, args.width, args.height)
    except KeyboardInterrupt:
        print("\nSimulation terminated by user.")
        pygame.quit()
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        pygame.quit()
        raise
