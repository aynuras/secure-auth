import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-confirmation-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './confirmation-modal.component.html',
})
export class ConfirmationModalComponent {
  @Input() isOpen = false;
  @Input() title = 'Onaylıyor musunuz?';
  @Input() message = 'Bu işlemi gerçekleştirmek istediğinize emin misiniz?';
  @Input() confirmText = 'Onayla';
  @Input() cancelText = 'Vazgeç';
  @Input() type: 'info' | 'success' | 'warning' | 'danger' = 'info';

  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();

  onConfirm() {
    this.confirm.emit();
  }

  onCancel() {
    this.cancel.emit();
  }
}
