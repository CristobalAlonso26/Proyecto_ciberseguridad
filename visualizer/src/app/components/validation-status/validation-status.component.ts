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

  get hasWarnings(): boolean {
    return this.validation.warnings.length > 0;
  }
}
