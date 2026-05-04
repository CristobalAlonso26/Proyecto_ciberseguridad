import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ValidationMetadata } from '../../models/analysis.model';

@Component({
  selector: 'app-validation-status',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './validation-status.component.html',
  styleUrl: './validation-status.component.css',
})
export class ValidationStatusComponent {
  @Input() validation: ValidationMetadata = { warnings: [], invalid_files: [] };

  open = false;

  get hasWarnings(): boolean {
    return this.validation.warnings.length > 0;
  }

  get hasInvalidFiles(): boolean {
    return this.validation.invalid_files.length > 0;
  }

  toggle(): void {
    this.open = !this.open;
  }
}
