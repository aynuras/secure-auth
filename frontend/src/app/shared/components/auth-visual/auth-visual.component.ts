import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FloatingCardsComponent } from '../floating-cards/floating-cards.component';

@Component({
  selector: 'app-auth-visual',
  standalone: true,
  imports: [CommonModule, FloatingCardsComponent],
  templateUrl: './auth-visual.component.html',
  styles: [':host { display: block; height: 100%; width: 100%; }'],
})
export class AuthVisualComponent {}
