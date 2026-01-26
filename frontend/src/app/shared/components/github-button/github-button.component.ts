import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-github-button',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './github-button.component.html',
})
export class GithubButtonComponent {
  @Input() label: string = 'Button';
  @Input() link: string = '#';
}
