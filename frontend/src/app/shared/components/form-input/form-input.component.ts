import { CommonModule } from '@angular/common';
import { Component, Input, forwardRef } from '@angular/core';
import {
  ControlValueAccessor,
  NG_VALUE_ACCESSOR,
  ReactiveFormsModule,
  FormControl,
} from '@angular/forms';

@Component({
  selector: 'app-form-input',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './form-input.component.html',
  styles: [':host { display: block; }'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => FormInputComponent),
      multi: true,
    },
  ],
})
export class FormInputComponent implements ControlValueAccessor {
  @Input() label: string = '';
  @Input() type: string = 'text';
  @Input() placeholder: string = '';
  @Input() id: string = '';
  @Input() control: FormControl | null = null;
  @Input() errorMessage: string = '';
  @Input() showPasswordStrength: boolean = false;

  value: string = '';
  isDisabled: boolean = false;
  isPasswordVisible: boolean = false;

  passwordStrength: 'Week' | 'Medium' | 'Strong' | null = null;
  strengthLabel: string = '';
  strengthColor: string = '';

  // Render type (handles password toggle)
  get inputType(): string {
    if (this.type === 'password') {
      return this.isPasswordVisible ? 'text' : 'password';
    }
    return this.type;
  }

  togglePasswordVisibility(): void {
    this.isPasswordVisible = !this.isPasswordVisible;
  }

  // Calculate generic password strength
  private calculateStrength(value: string): void {
    if (!value) {
      this.passwordStrength = null;
      return;
    }

    const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
    const hasNumber = /\d/.test(value);
    const hasMixed = /[a-z]/.test(value) && /[A-Z]/.test(value);
    const isLong = value.length >= 8;

    if (isLong && hasSpecial && (hasNumber || hasMixed)) {
      this.passwordStrength = 'Strong';
      this.strengthLabel = 'Güçlü';
      this.strengthColor = 'text-green-500';
    } else if (isLong && (hasNumber || hasMixed)) {
      this.passwordStrength = 'Medium';
      this.strengthLabel = 'Orta';
      this.strengthColor = 'text-yellow-500';
    } else {
      this.passwordStrength = 'Week';
      this.strengthLabel = 'Zayıf';
      this.strengthColor = 'text-red-500';
    }
  }

  onChange: (value: string) => void = () => {};
  onTouched: () => void = () => {};

  writeValue(value: string): void {
    this.value = value;
    if (this.showPasswordStrength) {
      this.calculateStrength(value);
    }
  }

  onInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.value = target.value;
    this.onChange(this.value);
    this.onTouched();

    if (this.showPasswordStrength) {
      this.calculateStrength(this.value);
    }
  }

  registerOnChange(fn: (value: string) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.isDisabled = isDisabled;
  }

  get showError(): boolean {
    return !!(this.control && this.control.invalid && this.control.touched);
  }
}
