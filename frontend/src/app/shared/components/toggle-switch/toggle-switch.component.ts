import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-toggle-switch',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './toggle-switch.component.html',
})
export class ToggleSwitchComponent {
  @Input() checked: boolean = false; // true/false durumu
  @Input() srLabel: string = 'Toggle'; // Erişilebilirlik (Screen Reader)
  @Output() changed = new EventEmitter<void>(); // Tıklandığında tetiklenir

  onToggle() {
    this.changed.emit();
  }
}
